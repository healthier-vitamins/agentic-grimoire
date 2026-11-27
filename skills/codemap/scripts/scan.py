# /// script
# requires-python = ">=3.11"
# ///
"""Scan a Python, JavaScript or TypeScript project and print the facts a code map needs.

Facts are what a script can count, so nobody writes them by hand: each source file's line
count, the project files it imports, its symbols with their line, and its state candidates
(enums, `Literal[...]` aliases, string unions, SQL `CHECK (col IN (...))` lists).

    uv run scan.py --root <project>    # writes <project>/.codemap/facts.json

Example: for `src/app/jobs.py` holding `Status = Literal["queued", "done"]` on line 9, the
facts hold `{"lines": 120, "symbols": {"Status": 9, ...}, "states":
[{"name": "Status", "line": 9, "values": ["queued", "done"]}], "imports": [...]}`.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import subprocess
from pathlib import Path

PYTHON = {".py"}
SCRIPT = {".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".mts", ".cts"}
SKIPPED_DIRS = {"node_modules", "dist", "build", "coverage", "__pycache__", "venv"}

SQL_CHECK = re.compile(r"CHECK\s*\(\s*(\w+)\s+IN\s*\(([^)]*)\)", re.IGNORECASE)
SQL_TABLE = re.compile(
    r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)", re.IGNORECASE
)
QUOTED = re.compile(r"""['"]([^'"]+)['"]""")
JS_IMPORT = re.compile(
    r"""(?:\bfrom\s*|\bimport\s*\(\s*|\brequire\s*\(\s*|^\s*import\s+)['"]([^'"]+)['"]""",
    re.MULTILINE,
)
JS_FUNCTION = re.compile(
    r"^(?:export\s+)?(?:default\s+)?(?:async\s+)?function\*?\s+(\w+)"
)
JS_CLASS = re.compile(
    r"^(\s*)(?:export\s+)?(?:default\s+)?(?:abstract\s+)?class\s+(\w+)"
)
JS_CONST = re.compile(r"^(?:export\s+)?(?:const|let|var)\s+(\w+)\s*[:=]")
JS_METHOD = re.compile(
    r"^\s+(?:static\s+)?(?:async\s+)?(?:get\s+|set\s+)?(\w+)\s*\(.*\)\s*(?::[^{]*)?\{\s*$"
)
JS_UNION = re.compile(
    r"^(?:export\s+)?type\s+(\w+)\s*=\s*((?:\s*\|?\s*['\"][^'\"]+['\"])+)\s*;?\s*$"
)
JS_ENUM = re.compile(
    r"^(?:export\s+)?(?:const\s+)?enum\s+(\w+)\s*\{([^}]*)\}", re.MULTILINE
)
JS_KEYWORDS = {
    "if",
    "for",
    "while",
    "switch",
    "catch",
    "function",
    "return",
    "constructor",
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write <root>/.codemap/facts.json.")
    parser.add_argument("--root", required=True, help="the project root")
    root = Path(parser.parse_args(argv).root).resolve()
    facts = scan(root)
    out = prepare_out_dir(root) / "facts.json"
    out.write_text(json.dumps(facts, indent=1))
    total = sum(entry["lines"] for entry in facts["files"].values())
    print(f"{out}: {len(facts['files'])} files, {total} lines")
    return 0


def prepare_out_dir(root: Path) -> Path:
    """Makes `<root>/.codemap/` and, on first use, lists `.codemap/` in `.git/info/exclude`."""
    out = root / ".codemap"
    out.mkdir(exist_ok=True)
    found = subprocess.run(
        ["git", "rev-parse", "--git-path", "info/exclude"],
        cwd=root, capture_output=True, text=True, check=False,
    )  # fmt: skip
    if found.returncode == 0:
        exclude = (root / found.stdout.strip()).resolve()
        lines = exclude.read_text().splitlines() if exclude.exists() else []
        if ".codemap/" not in lines:
            exclude.parent.mkdir(parents=True, exist_ok=True)
            exclude.write_text("\n".join([*lines, ".codemap/"]) + "\n")
    return out


def scan(root: Path) -> dict:
    """Every source file under `root`, keyed by its path relative to `root`."""
    paths = source_files(root)
    python_modules = python_module_index(paths)
    files = {}
    for path in paths:
        text = (root / path).read_text(errors="replace")
        suffix = Path(path).suffix
        if suffix in PYTHON:
            symbols, states, imports = python_facts(path, text, python_modules)
        else:
            symbols, states, imports = script_facts(path, text, set(paths))
        states += sql_states(text)
        files[path] = {
            "lines": text.count("\n") + (0 if text.endswith("\n") or not text else 1),
            "symbols": symbols,
            "states": sorted(states, key=lambda state: state["line"]),
            "imports": sorted(set(imports) - {path}),
        }
    return {"root": str(root), "files": files}


def source_files(root: Path) -> list[str]:
    """Git's view when `root` is in a repo (tracked plus untracked, minus ignored), else a
    walk that skips dot folders and build output."""
    listed = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=root, capture_output=True, text=True, check=False,
    )  # fmt: skip
    if listed.returncode == 0:
        candidates = listed.stdout.splitlines()
    else:
        candidates = []
        for folder, dirs, names in os.walk(root):
            dirs[:] = [
                d for d in dirs if not d.startswith(".") and d not in SKIPPED_DIRS
            ]
            candidates += [
                str((Path(folder) / name).relative_to(root)) for name in names
            ]
    return sorted(
        path for path in candidates
        if Path(path).suffix in PYTHON | SCRIPT and (root / path).is_file()
    )  # fmt: skip


# ---- Python -----------------------------------------------------------------------------------


def python_module_index(paths: list[str]) -> dict[str, str]:
    """Dotted module name -> file. A leading folder that is not a package (no `__init__.py`,
    like `src`) is dropped, the way it is dropped from `sys.path` imports.

    Example: `src/familiar/gateway.py` -> {"src.familiar.gateway", "familiar.gateway"}.
    """
    packages = {
        str(Path(path).parent) for path in paths if path.endswith("__init__.py")
    }
    index = {}
    for path in paths:
        if not path.endswith(".py"):
            continue
        parts = list(Path(path).with_suffix("").parts)
        if parts[-1] == "__init__":
            parts.pop()
        for start in range(len(parts)):
            index.setdefault(".".join(parts[start:]), path)
            if "/".join(parts[: start + 1]) in packages:
                break
    return index


def python_facts(
    path: str, text: str, modules: dict[str, str]
) -> tuple[dict, list, list]:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return {}, [], []
    symbols: dict[str, int] = {}
    states: list[dict] = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            symbols[node.name] = node.lineno
        elif isinstance(node, ast.ClassDef):
            symbols[node.name] = node.lineno
            for member in node.body:
                if isinstance(member, ast.FunctionDef | ast.AsyncFunctionDef):
                    symbols[f"{node.name}.{member.name}"] = member.lineno
            if any(_name_of(base).endswith(("Enum", "Flag")) for base in node.bases):
                states.append(
                    {
                        "name": node.name,
                        "line": node.lineno,
                        "values": _enum_values(node),
                    }
                )
        elif literal := _literal_alias(node):
            symbols[literal["name"]] = node.lineno
            states.append(literal)
        elif isinstance(node, ast.Assign | ast.AnnAssign):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            symbols.update(
                {t.id: node.lineno for t in targets if isinstance(t, ast.Name)}
            )
    package = _package_of(path, modules)
    imports = [
        found for name in _imported_names(tree, package) if (found := modules.get(name))
    ]
    return symbols, states, imports


def _literal_alias(node: ast.stmt) -> dict | None:
    """`Status = Literal["a", "b"]`, `Status: TypeAlias = Literal[...]` or `type Status = ...`."""
    if isinstance(node, ast.Assign) and len(node.targets) == 1:
        target, value = node.targets[0], node.value
    elif isinstance(node, ast.AnnAssign) and node.value is not None:
        target, value = node.target, node.value
    elif isinstance(node, ast.TypeAlias):
        target, value = node.name, node.value
    else:
        return None
    if not (isinstance(target, ast.Name) and isinstance(value, ast.Subscript)):
        return None
    if _name_of(value.value) != "Literal":
        return None
    items = value.slice.elts if isinstance(value.slice, ast.Tuple) else [value.slice]
    values = [item.value for item in items if isinstance(item, ast.Constant)]
    if not all(isinstance(value, str) for value in values):
        return None
    return {"name": target.id, "line": node.lineno, "values": values}


def _enum_values(node: ast.ClassDef) -> list[str]:
    """A member's string value when it has one, else its name."""
    values = []
    for member in node.body:
        if isinstance(member, ast.Assign) and isinstance(member.targets[0], ast.Name):
            constant = member.value
            is_text = isinstance(constant, ast.Constant) and isinstance(
                constant.value, str
            )
            values.append(constant.value if is_text else member.targets[0].id)
    return values


def _name_of(node: ast.expr) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return ""


def _package_of(path: str, modules: dict[str, str]) -> str:
    """The dotted package a file sits in, for relative imports: the shortest name it has."""
    names = [name for name, file in modules.items() if file == path]
    name = min(names, key=len) if names else ""
    return name if path.endswith("__init__.py") else name.rpartition(".")[0]


def _imported_names(tree: ast.Module, package: str) -> list[str]:
    """Each import as the most specific module name that could hold it.

    Example: in package `familiar`, `from .memory import Memory` yields `familiar.memory.Memory`
    and `familiar.memory`; the caller keeps whichever is a project file.
    """
    names = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                parts = alias.name.split(".")
                names += [".".join(parts[:end]) for end in range(len(parts), 0, -1)]
        elif isinstance(node, ast.ImportFrom):
            base = node.module or ""
            if node.level:
                anchor = package.split(".") if package else []
                anchor = (
                    anchor[: len(anchor) - (node.level - 1)]
                    if node.level > 1
                    else anchor
                )
                base = ".".join([*anchor, base] if base else anchor)
            names += [
                f"{base}.{alias.name}" if base else alias.name for alias in node.names
            ]
            names.append(base)
    return names


# ---- JavaScript and TypeScript ----------------------------------------------------------------


def script_facts(path: str, text: str, project: set[str]) -> tuple[dict, list, list]:
    """Line-based: top-level functions, classes, consts and class methods. shortcut: regexes,
    not a parser, so odd formatting can hide a symbol; switch to a real parser if maps miss
    entry points."""
    symbols: dict[str, int] = {}
    states: list[dict] = []
    class_name, class_indent = None, -1
    for number, line in enumerate(text.splitlines(), start=1):
        indent = len(line) - len(line.lstrip())
        if line.strip() and indent <= class_indent and not line.strip().startswith("}"):
            class_name, class_indent = None, -1
        if found := JS_CLASS.match(line):
            class_name, class_indent = found.group(2), len(found.group(1))
            symbols[class_name] = number
        elif found := JS_FUNCTION.match(line) or JS_CONST.match(line):
            symbols[found.group(1)] = number
        elif (
            class_name
            and (found := JS_METHOD.match(line))
            and found.group(1) not in JS_KEYWORDS
        ):
            symbols[f"{class_name}.{found.group(1)}"] = number
        if found := JS_UNION.match(line):
            states.append(
                {
                    "name": found.group(1),
                    "line": number,
                    "values": QUOTED.findall(found.group(2)),
                }
            )
    for found in JS_ENUM.finditer(text):
        members = [m.strip() for m in found.group(2).split(",") if m.strip()]
        values = [
            QUOTED.findall(m)[0] if QUOTED.findall(m) else m.split("=")[0].strip()
            for m in members
        ]
        states.append(
            {
                "name": found.group(1),
                "line": text.count("\n", 0, found.start()) + 1,
                "values": values,
            }
        )
    imports = [
        found
        for spec in JS_IMPORT.findall(text)
        if (found := _resolve_script(path, spec, project))
    ]
    return symbols, states, imports


def _resolve_script(path: str, spec: str, project: set[str]) -> str | None:
    """A relative import to the project file it loads; packages resolve to None.

    Example: `./store.js` from `src/app.ts` -> `src/store.ts` (TypeScript's ESM spelling)."""
    if not spec.startswith("."):
        return None
    base = os.path.normpath(os.path.join(os.path.dirname(path), spec))
    stem = base.rsplit(".", 1)[0] if Path(base).suffix in SCRIPT else base
    tries = (
        [base]
        + [stem + ext for ext in sorted(SCRIPT)]
        + [f"{base}/index{ext}" for ext in sorted(SCRIPT)]
    )
    return next((candidate for candidate in tries if candidate in project), None)


# ---- SQL in any file --------------------------------------------------------------------------


def sql_states(text: str) -> list[dict]:
    """`CHECK (status IN ('a', 'b'))` inside SQL text, named `<table>.<column>`.

    Example: a `CREATE TABLE turns (... status TEXT CHECK (status IN ('queued', 'done')))`
    yields {"name": "turns.status", "values": ["queued", "done"], "line": <line of CHECK>}.
    """
    states = []
    for found in SQL_CHECK.finditer(text):
        tables = SQL_TABLE.findall(text, 0, found.start())
        name = f"{tables[-1]}.{found.group(1)}" if tables else found.group(1)
        line = text.count("\n", 0, found.start()) + 1
        states.append(
            {"name": name, "line": line, "values": QUOTED.findall(found.group(2))}
        )
    return states


if __name__ == "__main__":
    raise SystemExit(main())
