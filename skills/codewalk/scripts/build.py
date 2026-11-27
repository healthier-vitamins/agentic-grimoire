# /// script
# requires-python = ">=3.11"
# dependencies = ["pygments>=2.17"]
# ///
"""Build the codewalk page: every workflow's walkthrough beside its recording, and the source
of every file they touch, inlined into one HTML file.

    uv run build.py --root <project> --title "Upload retry" [--section <slug>]

Reads  <out>/walkthrough/<workflow>.json   (the agent writes it)
       <out>/recordings/<workflow>.json    (a recorder writes it)
Writes <out>/page.html and <out>/texts.json, where <out> is <root>/.codewalk/<slug>, or
<root>/.codewalk without --section. Prints where each walkthrough step anchored, and every
variable it hid. Both inputs are specified in `references/page-format.md`.
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
_CHAPTER_STEPS = 7  # most steps one chapter may hold
_STEP_TEXTS = (
    "title",
    "gist",
    "where",
    "what",
    "run",
)  # every step needs these; `why` is optional
_SIZE_LIMIT = 14 * 1024 * 1024  # bytes; an artifact holds 16 MB
# Characters of one value the page shows; the rest stays in .codewalk/texts.json, which the
# page's "ask" link names, so a Claude Code session in the project can read the exact value.
_PAGE_TEXT_LIMIT = 20_000
# Name parts that mark a secret.
_SECRET_PARTS = {"token", "secret", "password", "passwd", "pwd", "auth", "authorization",
                 "credential", "credentials", "cookie", "apikey", "jwt", "bearer"}  # fmt: skip
# `key` marks a secret only after one of these words (`api_key`, `privateKey`): most names that
# end in `key` (`cache_key`, `idempotency_key`, `session_key`) are lookup keys, not secrets.
_SECRET_KEY_KINDS = {"api", "private", "secret", "access", "signing", "encryption", "client",
                     "master", "license", "service", "account", "ssh", "hmac", "app"}  # fmt: skip
# A quoted value printed after a name, inside a bigger value: `api_key='…'`, `"token": "…"`.
_QUOTED_FIELD = re.compile(r"""(\w+)(['"]?\s*[=:]\s*)('[^'\n]+'|"[^"\n]+")""")
# Credentials recognisable by shape alone, whatever holds them.
_SECRET_SHAPES = re.compile(
    r"(?<![\w-])(?:sk-[A-Za-z0-9_-]{16,}|AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{30,}"
    r"|xox[abprs]-[A-Za-z0-9-]{10,}|Bearer [A-Za-z0-9._~+/=-]{16,})"
)


class BuildError(Exception):
    """An input breaks page-format.md; the message names the file and what to fix."""


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    root = Path(args.root).resolve()
    out_dir = root / ".codewalk" / (args.section or "")
    texts_path = out_dir.relative_to(root).as_posix() + "/texts.json"
    try:
        workflows = _load_workflows(out_dir)
        files = _source_files(root, workflows)
        problems = [
            problem
            for workflow in workflows
            for problem in _walkthrough_problems(files, workflow)
        ]
        if problems:
            raise BuildError("\n".join(problems))
        hidden = _hide_secrets(workflows)
        for workflow in workflows:
            _anchor_steps(workflow)
    except BuildError as error:
        print(f"build failed:\n{error}", file=sys.stderr)
        return 1
    data = _page_data(files, workflows)
    texts = data["texts"]
    data["texts"] = [_page_text(text, texts_path) for text in texts]
    data["texts_path"] = texts_path
    page = _render(args.title, data)
    size = len(page.encode())
    if size > _SIZE_LIMIT:
        print(f"build failed: page is {size / 1e6:.1f} MB, over 14 MB. Narrow --watch and re-record.",
              file=sys.stderr)  # fmt: skip
        return 1
    out = out_dir / "page.html"
    out.write_text(page)
    (out_dir / "texts.json").write_text(json.dumps(texts))
    print(f"{out}: {len(workflows)} workflow(s), {size / 1e6:.1f} MB")
    print("hidden: " + (", ".join(sorted(hidden)) if hidden else "nothing"))
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    parser.add_argument(
        "--root", required=True, help="the project root holding .codewalk/"
    )
    parser.add_argument("--title", required=True, help="the page title")
    parser.add_argument(
        "--section",
        help="the codemap section slug: read and write .codewalk/<slug>/ instead of .codewalk/",
    )
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
            *(step["path"] for step in _steps(walkthrough)),
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


def _steps(walkthrough: dict[str, Any]) -> list[dict[str, Any]]:
    """Every walkthrough step in reading order, across its chapters."""
    return [
        step
        for chapter in walkthrough.get("chapters", [])
        for step in chapter.get("steps", [])
    ]


def _walkthrough_problems(
    files: dict[str, Path], workflow: dict[str, Any]
) -> list[str]:
    """Every chapter holds 1 to 7 steps, every step has its texts and a range inside a file the
    recording ran, and every function and breakpoint names real code."""
    key, walkthrough, recording = (
        workflow["key"],
        workflow["walkthrough"],
        workflow["recording"],
    )
    ran = {frame["path"] for frame in recording["frames"]}
    called = {frame["function"] for frame in recording["frames"]}
    chapters = walkthrough.get("chapters")
    if not isinstance(chapters, list) or not chapters:
        return [f"{key}: needs `chapters`, a list of {{title, steps}}"]
    problems = []
    for chapter_number, chapter in enumerate(chapters, start=1):
        steps = chapter.get("steps", [])
        if not chapter.get("title"):
            problems.append(f"{key} chapter {chapter_number}: needs a title")
        if not 1 <= len(steps) <= _CHAPTER_STEPS:
            problems.append(
                f"{key} chapter {chapter_number}: has {len(steps)} steps; give it 1 to "
                f"{_CHAPTER_STEPS}, and split a longer one into two chapters"
            )
        for step_number, step in enumerate(steps, start=1):
            where = f"{key} step {chapter_number}.{step_number} ({step['path']}:{step['from']}-{step['to']})"
            missing = [name for name in _STEP_TEXTS if not step.get(name)]
            if missing:
                problems.append(f"{where}: needs {', '.join(missing)}")
            if "caption" in step:
                problems.append(
                    f"{where}: `caption` is replaced by `where`, `what`, `run`, `why`"
                )
            if "call" in step and not (
                isinstance(step["call"], int) and step["call"] >= 1
            ):
                problems.append(f"{where}: `call` must be a whole number from 1")
            if step["path"] not in ran:
                problems.append(f"{where}: the recording never ran this file")
            elif (
                not 1 <= step["from"] <= step["to"] <= _line_count(files[step["path"]])
            ):
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


# ---- anchor each walkthrough step to one call -------------------------------------------------


def _anchor_steps(workflow: dict[str, Any]) -> None:
    """Give each walkthrough step its stop (`anchor`, a recording step index, or None when its
    lines never ran) and its `values`, then print which call it anchored to, with that call's
    arguments, so the walkthrough's author can check the step shows the call they meant.

    A step's call is the `call`-th call (1-based) of the function around `from`; without
    `call`, the first call that runs the step's lines. The stop is that call's first step on
    the step's lines. The values are that call's variables once it has run the step's last
    line it reaches, plus its return value unless that is None.
    """
    key, recording = workflow["key"], workflow["recording"]
    frames, steps, values = recording["frames"], recording["steps"], recording["values"]
    problems = []
    for chapter_number, chapter in enumerate(
        workflow["walkthrough"]["chapters"], start=1
    ):
        for step_number, step in enumerate(chapter["steps"], start=1):
            label = f'{key} {chapter_number}.{step_number} "{step["title"]}"'
            calls = _calls_of_owner(frames, steps, step)
            hits = {
                frame: [
                    index
                    for index in indexes
                    if step["from"] <= steps[index][1] <= step["to"]
                ]
                for frame, indexes in calls.items()
            }
            ran = [frame for frame in calls if hits[frame]]
            if "call" in step:
                if step["call"] > len(calls):
                    problems.append(
                        f"{label}: `call` is {step['call']}, but the function around line "
                        f"{step['from']} was called {len(calls)} time(s)"
                    )
                    continue
                frame = list(calls)[step["call"] - 1]
                if not hits[frame]:
                    problems.append(
                        f"{label}: call {step['call']} never ran lines {step['from']}-{step['to']}"
                    )
                    continue
            elif ran:
                frame = ran[0]
            else:
                step["anchor"], step["values"] = None, []
                print(
                    f"{label}: lines {step['from']}-{step['to']} never ran; no stop, no values"
                )
                continue
            step["anchor"] = hits[frame][0]
            step["values"] = _values_after(steps, values, calls[frame], hits[frame][-1])
            shown = {name for name, _value in step["values"]}
            for name in (*step.get("came_in", []), *step.get("went_out", [])):
                if name not in shown:
                    problems.append(
                        f"{label}: `{name}` in came_in/went_out is not among its values: "
                        f"{', '.join(sorted(shown)) or 'none'}"
                    )
            number = list(calls).index(frame) + 1
            print(
                f"{label}: {frames[frame]['function']} call {number} of {len(calls)}, "
                f"stop at recording step {step['anchor'] + 1}; arguments: "
                f"{_arguments(steps[calls[frame][0]], values)}"
            )
    if problems:
        raise BuildError("\n".join(problems))


def _calls_of_owner(
    frames: list[dict[str, Any]], steps: list[list[Any]], step: dict[str, Any]
) -> dict[int, list[int]]:
    """Each call of the innermost recorded function around the step's `from` line, in call
    order, with the indexes of its recording steps. A range that starts on a nested `def` is
    about that nested function: its enclosing function runs the `def` line when it only makes
    the closure. With no recorded function around `from`, every call in the file counts."""
    around = [
        frame
        for frame in frames
        if frame["path"] == step["path"]
        and frame["start"] <= step["from"] <= frame["end"]
    ]
    owner = min(around, key=lambda frame: frame["end"] - frame["start"], default=None)
    calls: dict[int, list[int]] = {}
    for index, (frame_index, *_rest) in enumerate(steps):
        frame = frames[frame_index]
        if frame["path"] != step["path"]:
            continue
        if owner and (frame["start"], frame["end"]) != (owner["start"], owner["end"]):
            continue
        calls.setdefault(frame_index, []).append(index)
    return calls


def _values_after(
    steps: list[list[Any]], values: list[str], call: list[int], last_hit: int
) -> list[tuple[str, str]]:
    """The call's variables once its line `last_hit` has run, as (name, printed value): its own
    next step records what that line changed. The receiver's attributes are left out."""
    later = [index for index in call if index > last_hit]
    state: dict[str, str] = {}
    returned = None
    for index in call:
        for name, value in steps[index][3].items():
            if name == "(return value)":
                returned = values[value] if value != GONE else None
            elif index <= (later[0] if later else last_hit) and not name.startswith(
                "("
            ):
                if value == GONE:
                    state.pop(name, None)
                elif not re.match(r"(self|this)(\.|$)", name):
                    state[name] = values[value]
    if returned is not None and returned != "None":
        state["(return value)"] = returned
    return list(state.items())


def _arguments(call_step: list[Any], values: list[str]) -> str:
    """A call's arguments on one line, each cut to 80 characters."""
    parts = []
    for name, value in call_step[3].items():
        if (
            value == GONE
            or re.match(r"(self|this)(\.|$)", name)
            or name.startswith("(")
        ):
            continue
        text = " ".join(values[value].split())
        parts.append(f"{name}={text[:80]}{'…' if len(text) > 80 else ''}")
    return ", ".join(parts) or "none"


# ---- hide secrets -------------------------------------------------------------------------------


def _hide_secrets(workflows: list[dict[str, Any]]) -> set[str]:
    """Hide every value whose variable name marks a secret, every field inside a value whose
    name does (a settings object's `api_key`), every credential recognisable by its shape, and
    every appearance of a secret environment variable's value. Returns what was hidden, for
    the user to check."""
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
            values[index] = _hide_secrets_inside(text, hidden)
        values.append(HIDDEN)
        for step in recording["steps"]:
            changed = step[3]
            for name, value in changed.items():
                if value != GONE and _is_secret_name(name):
                    changed[name] = len(values) - 1
                    hidden.add(name)
    return hidden


def _hide_secrets_inside(text: str, hidden: set[str]) -> str:
    def field(match: re.Match[str]) -> str:
        name, separator, _value = match.groups()
        if not _is_secret_name(name):
            return match.group(0)
        hidden.add(f"field {name} (inside printed values)")
        return f"{name}{separator}{HIDDEN}"

    def shape(match: re.Match[str]) -> str:
        hidden.add(
            f"a credential shaped like {match.group(0)[:4]}… (inside printed values)"
        )
        return HIDDEN

    return _SECRET_SHAPES.sub(shape, _QUOTED_FIELD.sub(field, text))


def _is_secret_name(name: str) -> bool:
    """Whether a variable or field name marks a secret.

    >>> [_is_secret_name(n) for n in ("api_key", "privateKey", "OPENAI_API_KEY", "auth_token")]
    [True, True, True, True]
    >>> [_is_secret_name(n) for n in ("key", "cache_key", "idempotency_key", "session_key")]
    [False, False, False, False]
    """
    parts = [
        part.lower() for part in re.findall(r"[A-Z]?[a-z0-9]+|[A-Z]+(?![a-z])", name)
    ]
    return any(part in _SECRET_PARTS for part in parts) or (
        len(parts) > 1 and parts[-1] == "key" and parts[-2] in _SECRET_KEY_KINDS
    )


# ---- page data ----------------------------------------------------------------------------------


def _page_text(text: str, texts_path: str) -> str:
    if len(text) <= _PAGE_TEXT_LIMIT:
        return text
    rest = len(text) - _PAGE_TEXT_LIMIT
    return f"{text[:_PAGE_TEXT_LIMIT]}\n… ({rest} more characters in {texts_path})"


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
    chapters = [
        {
            "title": chapter["title"],
            "steps": [
                {
                    **{name: step[name] for name in ("path", "from", "to", "anchor")},
                    **{name: step.get(name) or "" for name in (*_STEP_TEXTS, "why")},
                    "came_in": step.get("came_in", []),
                    "went_out": step.get("went_out", []),
                    "values": [
                        [texts.index(name), texts.index(value)]
                        for name, value in step["values"]
                    ],
                }
                for step in chapter["steps"]
            ],
        }
        for chapter in walkthrough["chapters"]
    ]
    return {
        "key": workflow["key"],
        "title": walkthrough.get("title", workflow["key"]),
        "summary": walkthrough.get("summary", ""),
        "fakes": walkthrough.get("fakes", []),
        "breakpoints": walkthrough.get("breakpoints", []),
        "chapters": chapters,
        "language": recording["language"],
        "entry": recording["entry"],
        "exit": recording["exit"],
        "truncated": recording["truncated"],
        "recorder_ms": recording.get("recorder_ms"),
        "exact_values": recording.get("exact_values", True),
        "staged": recording.get("staged", []),
        "frames": recording["frames"],
        "steps": _packed_steps(steps, recording["values"], texts),
    }


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
