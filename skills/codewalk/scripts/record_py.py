"""Record one run of a Python workflow the way a time-travel debugger replays it: one step for
every line, call, await, resume and return in the watched files, each with the variables that
changed since that frame's previous step, printed the way `print` would show them.

    <project python> record_py.py --root . --watch src/upload \\
        --entry tests/test_upload.py::test_retry --out .codewalk/recordings/upload.json \\
        [--staging .codewalk/staging/retry]

The entry is a pytest node id or a driver script. With `--staging`, a staged file is imported in
place of the project's file at the same path (`references/staging.md`). It runs in this process under
`sys.monitoring` (PEP 669, Python 3.12+), so the project carries no tracing code. Code outside
`--watch` runs unrecorded, like a debugger's "just my code". The output's shape is in
`references/page-format.md`.
"""

from __future__ import annotations

import argparse
import ast
import asyncio
import dataclasses
import importlib.abc
import importlib.util
import inspect
import json
import os
import platform
import runpy
import sys
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from enum import Enum
from functools import cache
from importlib.machinery import ModuleSpec
from pathlib import Path
from types import CodeType, FrameType, ModuleType
from typing import Any

__all__ = ["main", "record"]

GONE = -1  # a variable that left the frame since its previous step
_LINE_WIDTH = 72
# Characters; a longer value is cut, as a debugger's variables panel cuts it.
_VALUE_LIMIT = 4000
_ITEM_LIMIT = 50  # items of one collection printed before "…"
_DEPTH_LIMIT = 4  # nesting printed before an object collapses to its type name


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    if sys.version_info < (3, 12):
        print(
            f"record_py needs Python 3.12+ for sys.monitoring; this is {platform.python_version()}.",
            file=sys.stderr,
        )
        return 2
    out = Path(args.out).resolve()  # before `record` moves into the project root
    root = Path(args.root).resolve()
    tree = _Tree(root, (root / args.staging).resolve() if args.staging else None)
    recording = record(tree, args.watch, args.entry, args.max_steps)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(recording))
    print(
        f"{out}: {len(recording['steps'])} steps in {len(recording['frames'])} calls; "
        f"exit {'ok' if recording['exit']['ok'] else 'FAILED'} ({recording['exit']['detail']})"
        + ("; TRUNCATED at --max-steps" if recording["truncated"] else "")
    )
    return 0


def record(tree: _Tree, watch: list[str], entry: str, max_steps: int) -> dict[str, Any]:
    """Run `entry` inside the project root, staged files first, and return its recording."""
    os.chdir(tree.root)
    sys.path.insert(0, str(tree.root))
    if tree.staging:
        sys.path.append(str(tree.staging))  # staged-only top-level modules
        sys.meta_path.insert(0, _StagingFinder(tree))
    recorder = _Recorder(tree, tree.watched_prefixes(watch), max_steps)
    with recorder.listening():
        exit_status = _run_entry(entry)
    return {
        "version": 1,
        "language": "python",
        "entry": {"kind": _entry_kind(entry), "target": entry},
        "staging": tree.staging.relative_to(tree.root).as_posix()
        if tree.staging
        else None,
        "staged": tree.staged(),
        "exit": exit_status,
        "truncated": recorder.truncated,
        "frames": recorder.frames,
        "steps": recorder.steps,
        "values": recorder.values,
    }


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    parser.add_argument("--root", required=True, help="the project root")
    parser.add_argument(
        "--watch", nargs="+", required=True, help="files or folders to step through"
    )
    parser.add_argument(
        "--entry", required=True, help="a pytest node id or a driver script"
    )
    parser.add_argument("--out", required=True, help="where to write the recording")
    parser.add_argument(
        "--max-steps", type=int, default=50_000, help="stop recording after this many"
    )
    parser.add_argument(
        "--staging",
        help="a staging folder whose files replace the project's (prototype)",
    )
    return parser.parse_args(argv)


def _entry_kind(entry: str) -> str:
    name = Path(entry.split("::")[0]).name
    is_test = "::" in entry or name.startswith("test_") or name.endswith("_test.py")
    return "test" if is_test else "driver"


def _run_entry(entry: str) -> dict[str, Any]:
    if _entry_kind(entry) == "test":
        import pytest  # pyright: ignore[reportMissingImports]  # the project's own; drivers skip it

        code = pytest.main([entry, "-q", "-p", "no:cacheprovider"])
        return {"ok": code == 0, "detail": f"pytest exit code {int(code)}"}
    sys.argv = [entry]
    try:
        runpy.run_path(entry, run_name="__main__")
    except SystemExit as stop:
        return {"ok": stop.code in (None, 0), "detail": f"SystemExit({stop.code!r})"}
    except BaseException as error:  # noqa: BLE001 -- a failed run still records; the page shows it
        return {"ok": False, "detail": f"{type(error).__name__}: {error}"}
    return {"ok": True, "detail": "driver finished"}


# ---- the code that runs: the project, with staged files over it -------------------------------


@dataclasses.dataclass(frozen=True)
class _Tree:
    """The project root and, for a prototype, the staging folder mirroring its paths. A staged
    file replaces the project's file at the same path; a staged-only file adds one. Every path a
    recording names is the project path, staged or not."""

    root: Path
    staging: Path | None

    def staged(self) -> list[str]:
        if self.staging is None:
            return []
        return sorted(
            path.relative_to(self.staging).as_posix()
            for path in self.staging.rglob("*.py")
        )

    def project_path(self, filename: str) -> str:
        path = Path(filename)
        if self.staging and path.is_relative_to(self.staging):
            return path.relative_to(self.staging).as_posix()
        return path.relative_to(self.root).as_posix()

    def staged_twin(self, path: str) -> Path | None:
        """The staged file or folder at a project file's or folder's path, if there is one."""
        if self.staging is None:
            return None
        real = Path(path)
        if not real.is_relative_to(self.root) or real.is_relative_to(self.staging):
            return None
        twin = self.staging / real.relative_to(self.root)
        return twin if twin.exists() else None

    def watched_prefixes(self, watch: list[str]) -> tuple[str, ...]:
        """Each watched path under the root and under staging. A folder ends in a separator,
        so `src/up` never matches `src/upload.py`."""
        bases = [self.root] if self.staging is None else [self.root, self.staging]
        paths = [(base / path).resolve() for base in bases for path in watch]
        return tuple(
            str(path) + os.sep if path.is_dir() else str(path) for path in paths
        )


class _StagingFinder(importlib.abc.MetaPathFinder):
    """First on `sys.meta_path`: asks the finders after it, then swaps in the staged twin of
    what they found, and adds each project package's staged twin folder to its search path so
    staged-only modules import as if they were in the project."""

    def __init__(self, tree: _Tree) -> None:
        self._tree = tree

    def find_spec(
        self, fullname: str, path: Any, target: Any = None
    ) -> ModuleSpec | None:
        spec = self._found_by_the_rest(fullname, path, target)
        if spec is None:
            return None
        locations = spec.submodule_search_locations
        if isinstance(locations, list):
            for folder in list(locations):
                twin = self._tree.staged_twin(folder)
                if twin is not None and str(twin) not in locations:
                    locations.append(str(twin))
        twin = self._tree.staged_twin(spec.origin) if spec.origin else None
        if twin is None:
            return spec
        return importlib.util.spec_from_file_location(
            fullname, twin, submodule_search_locations=locations
        )

    def _found_by_the_rest(
        self, fullname: str, path: Any, target: Any
    ) -> ModuleSpec | None:
        for finder in sys.meta_path:
            find_spec = getattr(finder, "find_spec", None)
            if finder is self or find_spec is None:
                continue
            spec = find_spec(fullname, path, target)
            if spec is not None:
                return spec
        return None


# ---- the recorder: one sys.monitoring callback per kind of step ---------------------------------


_MONITOR = sys.monitoring  # pyright: ignore[reportAttributeAccessIssue]


class _Recorder:
    """Each callback is called from the frame it reports on, so `sys._getframe(1)` is that frame.
    Code a callback runs (a `__repr__` while printing) raises no events of its own."""

    def __init__(self, tree: _Tree, watched: tuple[str, ...], max_steps: int) -> None:
        self.frames: list[dict[str, Any]] = []
        self.steps: list[list[Any]] = []
        self.values: list[str] = []
        self.truncated = False
        self._tree = tree
        self._watched = watched
        self._max_steps = max_steps
        self._value_index: dict[str, int] = {}
        # Live frames only: a frame leaves at its return or unwind, so a reused frame object is
        # never mistaken for an old one.
        self._live: dict[FrameType, int] = {}
        # Frame -> its variables at its last step.
        self._printed: dict[int, dict[str, str]] = {}

    @contextmanager
    def listening(self) -> Iterator[None]:
        tool = _MONITOR.DEBUGGER_ID
        callbacks = self._callbacks()
        _MONITOR.use_tool_id(tool, "codewalk")
        for event, callback in callbacks.items():
            _MONITOR.register_callback(tool, event, callback)
        _MONITOR.set_events(tool, sum(callbacks))
        try:
            yield
        finally:
            _MONITOR.set_events(tool, 0)
            for event in callbacks:
                _MONITOR.register_callback(tool, event, None)
            _MONITOR.free_tool_id(tool)

    def _callbacks(self) -> dict[int, Any]:
        events = _MONITOR.events
        return {
            events.PY_START: self._on_start,
            events.LINE: self._on_line,
            events.PY_YIELD: self._on_yield,
            events.PY_RESUME: self._on_resume,
            events.PY_RETURN: self._on_return,
            events.RAISE: self._on_raise,
            events.PY_UNWIND: self._on_unwind,
        }

    def _on_start(self, code: CodeType, _offset: int) -> Any:
        if not self._is_watched(code):
            return _MONITOR.DISABLE
        frame = sys._getframe(1)
        index = len(self.frames)
        path = self._tree.project_path(code.co_filename)
        start, end = _enclosing_definition(code.co_filename, code.co_firstlineno)
        self.frames.append(
            {
                "function": f"{Path(code.co_filename).stem}.{code.co_qualname}",
                "path": path,
                "start": start,
                "end": end,
                "parent": self._caller_of(frame),
                "task": _task_name(),
            }
        )
        self._live[frame] = index
        self._printed[index] = {}
        self._add_step(frame, "call")
        return None

    def _on_line(self, code: CodeType, _line: int) -> Any:
        if not self._is_watched(code):
            return _MONITOR.DISABLE
        self._step_here("line")
        return None

    def _on_yield(self, code: CodeType, _offset: int, _value: Any) -> Any:
        if not self._is_watched(code):
            return _MONITOR.DISABLE
        self._step_here("await" if code.co_flags & inspect.CO_COROUTINE else "yield")
        return None

    def _on_resume(self, code: CodeType, _offset: int) -> Any:
        if not self._is_watched(code):
            return _MONITOR.DISABLE
        self._step_here("resume")
        return None

    def _on_return(self, code: CodeType, _offset: int, value: Any) -> Any:
        if not self._is_watched(code):
            return _MONITOR.DISABLE
        self._step_here("return", {"(return value)": _pretty(value)})
        self._leave(sys._getframe(1))
        return None

    def _on_raise(self, code: CodeType, _offset: int, exception: BaseException) -> None:
        # RAISE and PY_UNWIND cannot be disabled, so unwatched code just returns.
        if self._is_watched(code):
            self._step_here("raise", {"(raised)": repr(exception)})

    def _on_unwind(
        self, code: CodeType, _offset: int, exception: BaseException
    ) -> None:
        if self._is_watched(code):
            self._step_here("unwind", {"(raised)": repr(exception)})
            self._leave(sys._getframe(1))

    def _is_watched(self, code: CodeType) -> bool:
        """Functions only: a module or class body runs once at import and is setup, not the
        workflow. A generator expression runs on its parent's line, so it is part of it."""
        return (
            code.co_filename.startswith(self._watched)
            and bool(code.co_flags & inspect.CO_NEWLOCALS)
            and code.co_name != "<genexpr>"
        )

    def _step_here(self, kind: str, extra: Mapping[str, str] | None = None) -> None:
        """A step for the frame two calls up: the watched frame the callback reports on."""
        frame = sys._getframe(2)
        if frame in self._live:  # else it started before recording began
            self._add_step(frame, kind, extra)

    def _add_step(
        self, frame: FrameType, kind: str, extra: Mapping[str, str] | None = None
    ) -> None:
        if len(self.steps) >= self._max_steps:
            self.truncated = True
            _MONITOR.set_events(_MONITOR.DEBUGGER_ID, 0)
            return
        index = self._live[frame]
        printed = {**_variables(frame), **(extra or {})}
        before = self._printed[index]
        changed = {
            name: self._value(text)
            for name, text in printed.items()
            if before.get(name) != text
        }
        changed.update((name, GONE) for name in before.keys() - printed.keys())
        self._printed[index] = printed
        self.steps.append([index, frame.f_lineno, kind, changed])

    def _value(self, text: str) -> int:
        index = self._value_index.get(text)
        if index is None:
            index = self._value_index[text] = len(self.values)
            self.values.append(text)
        return index

    def _caller_of(self, frame: FrameType) -> int:
        """The nearest watched frame up the stack; -1 when none, as for an asyncio task's
        first frame, which only the event loop sits above."""
        caller = frame.f_back
        while caller is not None:
            if caller in self._live:
                return self._live[caller]
            caller = caller.f_back
        return -1

    def _leave(self, frame: FrameType) -> None:
        index = self._live.pop(frame, None)
        if index is not None:
            self._printed.pop(index, None)


def _enclosing_definition(filename: str, line: int) -> tuple[int, int]:
    """The innermost def or class around `line`, decorators included: what the code pane
    shows. A lambda has no def of its own, so it shows the def around it."""
    around = [
        (start, end) for start, end in _definitions(filename) if start <= line <= end
    ]
    return max(around, default=(line, line))  # innermost: the latest start


@cache
def _definitions(filename: str) -> list[tuple[int, int]]:
    ranges = []
    for node in ast.walk(ast.parse(Path(filename).read_text())):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            first = min([node.lineno, *(d.lineno for d in node.decorator_list)])
            ranges.append((first, node.end_lineno or node.lineno))
    return ranges


def _task_name() -> str:
    try:
        task = asyncio.current_task()
    except RuntimeError:  # no running loop: plain synchronous code
        return "main"
    return task.get_name() if task else "main"


def _variables(frame: FrameType) -> dict[str, str]:
    return {
        name: _pretty(value)
        for name, value in frame.f_locals.items()
        if not name.startswith("__")
    }


# ---- printing, the way `print` would show it, wrapped to fit a panel ----------------------------


def _pretty(value: Any) -> str:
    try:
        text = _pretty_at(value, 0)
    except Exception as error:  # noqa: BLE001 -- a broken __repr__ must not stop the recording
        text = f"<{type(value).__name__} (printing failed: {error!r})>"
    if len(text) > _VALUE_LIMIT:
        return f"{text[:_VALUE_LIMIT]}\n… ({len(text) - _VALUE_LIMIT} more characters)"
    return text


def _pretty_at(value: Any, depth: int) -> str:
    short = _short_form(value)
    if short is not None:
        return short
    if depth >= _DEPTH_LIMIT:
        return f"<{type(value).__name__} …>"
    fields = _fields_of(value)
    if fields is not None:
        return _call(type(value).__name__, fields, depth)
    if isinstance(value, Mapping):
        items = [
            f"{_pretty_at(k, depth + 1)}: {_pretty_at(v, depth + 1)}"
            for k, v in _first(value.items())
        ]
        return _bracket("{", _with_more(items, len(value)), "}")
    if isinstance(value, list | tuple | set | frozenset):
        open_, close = {list: "[]", tuple: "()"}.get(type(value), "{}")
        items = [_pretty_at(item, depth + 1) for item in _first(value)]
        return _bracket(open_, _with_more(items, len(value)), close)
    return repr(value)


def _short_form(value: Any) -> str | None:
    """Values that print as one token, and objects best collapsed to a name."""
    if value is None or isinstance(value, bool | int | float | complex | str | bytes):
        return repr(value)
    if isinstance(value, Enum):
        return f"{type(value).__name__}.{value.name}"
    if isinstance(value, asyncio.Task):
        return f"<Task {value.get_name()} {'done' if value.done() else 'pending'}>"
    if isinstance(value, ModuleType):
        return f"<module {value.__name__}>"
    if isinstance(value, type):
        return f"<class {value.__qualname__}>"
    if callable(value) and _fields_of(value) is None:
        return f"<function {getattr(value, '__qualname__', type(value).__name__)}>"
    return None


def _fields_of(value: Any) -> dict[str, Any] | None:
    """The state of a pydantic model, a dataclass, or a plain object with the default repr."""
    model_fields = getattr(type(value), "model_fields", None)
    if isinstance(model_fields, dict):
        return {name: getattr(value, name, None) for name in model_fields}
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return {
            f.name: getattr(value, f.name) for f in dataclasses.fields(value) if f.repr
        }
    if type(value).__repr__ is object.__repr__ and hasattr(value, "__dict__"):
        return dict(vars(value))
    return None


def _first(items: Any) -> list[Any]:
    return [item for _, item in zip(range(_ITEM_LIMIT), items, strict=False)]


def _with_more(items: list[str], total: int) -> list[str]:
    return [*items, f"… {total - len(items)} more"] if total > len(items) else items


def _call(name: str, fields: dict[str, Any], depth: int) -> str:
    parts = [f"{key}={_pretty_at(value, depth + 1)}" for key, value in fields.items()]
    return _bracket(f"{name}(", parts, ")")


def _bracket(open_: str, items: list[str], close: str) -> str:
    one_line = f"{open_}{', '.join(items)}{close}"
    if len(one_line) <= _LINE_WIDTH and "\n" not in one_line:
        return one_line
    body = ",\n".join(_indent(item) for item in items)
    return f"{open_}\n{body},\n{close}"


def _indent(text: str) -> str:
    return "\n".join("    " + line for line in text.split("\n"))


if __name__ == "__main__":
    sys.exit(main())
