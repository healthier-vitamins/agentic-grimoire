# /// script
# requires-python = ">=3.11"
# dependencies = ["pygments>=2.17"]
# ///
"""Build the codewalk page: every workflow's walkthrough beside its recording, and the source
of every file they touch, inlined into one HTML file.

    uv run build.py --root <project> --title "Upload retry"

Reads  <root>/.codewalk/walkthrough/<workflow>.json   (the agent writes it)
       <root>/.codewalk/recordings/<workflow>.json    (a recorder writes it)
Writes <root>/.codewalk/page.html, and prints every variable it hid.
Both inputs are specified in `references/page-format.md`.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

from pygments.lexer import Lexer
from pygments.lexers import TextLexer, get_lexer_for_filename
from pygments.token import STANDARD_TYPES, _TokenType
from pygments.util import ClassNotFound

__all__ = ["main"]

TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "template.html"
STEP_KINDS = ["call", "line", "await", "yield", "resume", "return", "raise", "unwind"]
GONE = -1
HIDDEN = "<hidden>"
_SIZE_LIMIT = 14 * 1024 * 1024  # bytes; an artifact holds 16 MB
# Name parts that mark a secret. `key` alone is a loop variable far more often than a secret,
# so it counts only as a suffix: `api_key`, `privateKey`.
_SECRET_PARTS = {"token", "secret", "password", "passwd", "pwd", "auth", "authorization",
                 "credential", "credentials", "cookie", "apikey", "jwt", "bearer"}  # fmt: skip


class BuildError(Exception):
    """An input breaks page-format.md; the message names the file and what to fix."""


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    root = Path(args.root).resolve()
    try:
        workflows = _load_workflows(root / ".codewalk")
        files = _source_files(root, workflows)
        problems = [
            problem
            for workflow in workflows
            for problem in _range_problems(files, workflow)
        ]
        if problems:
            raise BuildError("\n".join(problems))
    except BuildError as error:
        print(f"build failed:\n{error}", file=sys.stderr)
        return 1
    hidden = _hide_secrets(workflows)
    page = _render(args.title, _page_data(files, workflows))
    size = len(page.encode())
    if size > _SIZE_LIMIT:
        print(f"build failed: page is {size / 1e6:.1f} MB, over 14 MB. Narrow --watch and re-record.",
              file=sys.stderr)  # fmt: skip
        return 1
    out = root / ".codewalk" / "page.html"
    out.write_text(page)
    print(f"{out}: {len(workflows)} workflow(s), {size / 1e6:.1f} MB")
    print("hidden: " + (", ".join(sorted(hidden)) if hidden else "nothing"))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    parser.add_argument(
        "--root", required=True, help="the project root holding .codewalk/"
    )
    parser.add_argument("--title", required=True, help="the page title")
    return parser.parse_args(argv)


# ---- load and check -----------------------------------------------------------------------------


def _load_workflows(codewalk: Path) -> list[dict[str, Any]]:
    """One entry per workflow: its walkthrough and its recording, paired by file name."""
    walkthroughs = {
        path.stem: path for path in sorted((codewalk / "walkthrough").glob("*.json"))
    }
    recordings = {
        path.stem: path for path in sorted((codewalk / "recordings").glob("*.json"))
    }
    if not walkthroughs:
        raise BuildError(f"no walkthroughs in {codewalk / 'walkthrough'}")
    unpaired = walkthroughs.keys() ^ recordings.keys()
    if unpaired:
        raise BuildError(
            f"each workflow needs both files; unpaired: {', '.join(sorted(unpaired))}"
        )
    return [
        {
            "key": key,
            "walkthrough": _read_json(walkthroughs[key]),
            "recording": _read_json(recordings[key]),
        }
        for key in walkthroughs
    ]


def _read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as error:
        raise BuildError(f"{path}: not JSON ({error})") from error


def _source_files(root: Path, workflows: list[dict[str, Any]]) -> dict[str, Path]:
    """The file each project path on the page means: its staged twin when the recording ran
    staged code (`references/staging.md`), else the project's own."""
    files: dict[str, Path] = {}
    for workflow in workflows:
        recording, walkthrough = workflow["recording"], workflow["walkthrough"]
        staged = set(recording.get("staged", []))
        paths = (
            *(frame["path"] for frame in recording["frames"]),
            *(step["path"] for step in walkthrough.get("steps", [])),
            *(function["path"] for function in walkthrough.get("functions", [])),
        )
        for path in paths:
            file = root / recording["staging"] / path if path in staged else root / path
            if files.setdefault(path, file) != file:
                raise BuildError(
                    f"{path} means {files[path]} in one workflow and {file} in "
                    f"{workflow['key']}; record every workflow on one page from one staging"
                )
    return files


def _range_problems(files: dict[str, Path], workflow: dict[str, Any]) -> list[str]:
    """Every walkthrough range lies inside a file the recording ran, and every function and
    breakpoint names real code."""
    key, walkthrough, recording = (
        workflow["key"],
        workflow["walkthrough"],
        workflow["recording"],
    )
    ran = {frame["path"] for frame in recording["frames"]}
    called = {frame["function"] for frame in recording["frames"]}
    problems = []
    for number, step in enumerate(walkthrough.get("steps", []), start=1):
        where = f"{key} step {number} ({step['path']}:{step['from']}-{step['to']})"
        if step["path"] not in ran:
            problems.append(f"{where}: the recording never ran this file")
        elif not 1 <= step["from"] <= step["to"] <= _line_count(files[step["path"]]):
            problems.append(f"{where}: the range is outside the file")
    for function in walkthrough.get("functions", []):
        if not files[function["path"]].is_file():
            problems.append(
                f"{key} function {function['name']}: no file {function['path']}"
            )
    for name in walkthrough.get("breakpoints", []):
        if name not in called:
            problems.append(f"{key} breakpoint {name}: never called in the recording")
    return problems


def _line_count(path: Path) -> int:
    return len(path.read_text().splitlines())


# ---- hide secrets -------------------------------------------------------------------------------


def _hide_secrets(workflows: list[dict[str, Any]]) -> set[str]:
    """Hide every value whose variable name marks a secret, and every appearance of a secret
    environment variable's value. Returns what was hidden, for the user to check."""
    secret_env = {
        name: value
        for name, value in os.environ.items()
        if _is_secret_name(name) and len(value) >= 8
    }
    hidden: set[str] = set()
    for workflow in workflows:
        recording = workflow["recording"]
        values: list[str] = recording["values"]
        for index, text in enumerate(values):
            for name, secret in secret_env.items():
                if secret in text:
                    text = text.replace(secret, HIDDEN)
                    hidden.add(f"${name} (its value, wherever printed)")
            values[index] = text
        values.append(HIDDEN)
        for step in recording["steps"]:
            changed = step[3]
            for name, value in changed.items():
                if value != GONE and _is_secret_name(name):
                    changed[name] = len(values) - 1
                    hidden.add(name)
    return hidden


def _is_secret_name(name: str) -> bool:
    parts = [
        part.lower() for part in re.findall(r"[A-Z]?[a-z0-9]+|[A-Z]+(?![a-z])", name)
    ]
    return any(part in _SECRET_PARTS for part in parts) or (
        len(parts) > 1 and parts[-1] == "key"
    )


# ---- page data ----------------------------------------------------------------------------------


def _page_data(
    files: dict[str, Path], workflows: list[dict[str, Any]]
) -> dict[str, Any]:
    texts = _TextTable()
    return {
        "step_kinds": STEP_KINDS,
        "sources": {
            path: _highlighted_lines(file) for path, file in sorted(files.items())
        },
        "workflows": [_workflow_json(workflow, texts) for workflow in workflows],
        "texts": texts.texts,
    }


def _workflow_json(workflow: dict[str, Any], texts: _TextTable) -> dict[str, Any]:
    walkthrough, recording = workflow["walkthrough"], workflow["recording"]
    steps = recording["steps"]
    return {
        "key": workflow["key"],
        "title": walkthrough.get("title", workflow["key"]),
        "summary": walkthrough.get("summary", ""),
        "functions": walkthrough.get("functions", []),
        "fakes": walkthrough.get("fakes", []),
        "breakpoints": walkthrough.get("breakpoints", []),
        "walkthrough": [
            {**step, "at": _first_run(recording, step)}
            for step in walkthrough.get("steps", [])
        ],
        "language": recording["language"],
        "entry": recording["entry"],
        "exit": recording["exit"],
        "truncated": recording["truncated"],
        "staged": recording.get("staged", []),
        "frames": recording["frames"],
        "steps": _packed_steps(steps, recording["values"], texts),
    }


def _first_run(recording: dict[str, Any], step: dict[str, Any]) -> int | None:
    """The first recorded step on the walkthrough step's lines: where "next stop" lands."""
    frames = recording["frames"]
    for index, (frame, line, _kind, _changed) in enumerate(recording["steps"]):
        if frames[frame]["path"] == step["path"] and step["from"] <= line <= step["to"]:
            return index
    return None


class _TextTable:
    """Every variable name and printed value across all recordings, once each."""

    def __init__(self) -> None:
        self.texts: list[str] = []
        self._index: dict[str, int] = {}

    def index(self, text: str) -> int:
        found = self._index.get(text)
        if found is None:
            found = self._index[text] = len(self.texts)
            self.texts.append(text)
        return found


def _packed_steps(
    steps: list[list[Any]], values: list[str], texts: _TextTable
) -> list[int]:
    """Steps as one flat list of ints, about a third the size of objects: per step its frame,
    line, kind (an index into STEP_KINDS) and its number of changed variables, then a
    (name, value) pair of indexes into `texts` for each; a value of -1 means it left the frame."""
    packed: list[int] = []
    for frame, line, kind, changed in steps:
        packed += [frame, line, STEP_KINDS.index(kind), len(changed)]
        for name, value in changed.items():
            packed += [
                texts.index(name),
                GONE if value == GONE else texts.index(values[value]),
            ]
    return packed


# ---- sources, highlighted line by line ----------------------------------------------------------


def _highlighted_lines(path: Path) -> list[str]:
    """One HTML string per source line. Tokens are split at newlines, so a docstring spanning
    lines still closes its span on each one."""
    text = path.read_text()
    lines: list[list[str]] = [[]]
    for token, value in _lexer_for(path).get_tokens(text):
        css = _css_class(token)
        for number, piece in enumerate(value.split("\n")):
            if number:
                lines.append([])
            if piece:
                escaped = html.escape(piece, quote=False)
                lines[-1].append(
                    f'<span class="{css}">{escaped}</span>' if css else escaped
                )
    return ["".join(parts) for parts in lines][: len(text.splitlines())]


def _lexer_for(path: Path) -> Lexer:
    try:
        return get_lexer_for_filename(path.name, stripnl=False, ensurenl=False)
    except ClassNotFound:
        return TextLexer()


def _css_class(token: _TokenType) -> str:
    """Pygments' short class for the token, or its nearest parent's."""
    while token not in STANDARD_TYPES and token.parent is not None:
        token = token.parent
    return STANDARD_TYPES.get(token, "")


def _render(title: str, data: dict[str, Any]) -> str:
    payload = json.dumps(data, separators=(",", ":")).replace("</", "<\\/")
    page = TEMPLATE.read_text()
    return page.replace("__TITLE__", html.escape(title)).replace(
        "/*__DATA__*/null", payload
    )


if __name__ == "__main__":
    sys.exit(main())
