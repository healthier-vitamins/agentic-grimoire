# Page format

The two files `build.py` joins into the page, one pair per workflow, paired by file name:
`walkthrough/<workflow>.json` and `recordings/<workflow>.json`, both in the section's folder
`.codewalk/<section>/`. The page lists workflows in file-name order, so name them
`01-checkout`, `02-refund` to keep the confirmed map's order. Every path is relative to the
project root, with `/` separators. Lines are 1-based.

## Walkthrough — the agent writes it

```json
{
  "title": "Upload with retry",
  "summary": "One sentence: what the workflow does, from its entry to where it leaves.",
  "functions": [
    { "name": "upload.upload_file", "path": "src/upload.py", "line": 12 },
    { "name": "upload._send_chunk", "path": "src/upload.py", "line": 40 }
  ],
  "fakes": ["s3.put_object: fake, the user's pick (writes to the shared bucket)"],
  "chapters": [
    { "title": "The upload starts", "steps": [
      { "path": "src/upload.py", "from": 12, "to": 18, "title": "The file is opened",
        "gist": "The upload opens 'a.bin' and splits it into 3 chunks.",
        "where": "…", "what": "…", "run": "…", "why": "…",
        "came_in": ["path"] },
      { "path": "src/upload.py", "from": 40, "to": 52, "title": "The second try succeeds",
        "gist": "…", "where": "…", "what": "…", "run": "…",
        "call": 2, "went_out": ["(return value)"] }
    ] }
  ],
  "breakpoints": ["upload._send_chunk"]
}
```

- `functions` — the map the user confirmed, in call order. `name` is `module.qualname`, the
  same form a recording's frames use.
- `fakes` — one line per faked call: what, and why. Empty when every call ran for real.
- `chapters` — the walkthrough in reading order. A chapter is one idea of the workflow, with
  a `title` and 1 to 7 `steps`; the build fails on a chapter with more. Split a longer idea
  into two chapters.
- A **step** is one range of code. `path`, `from`, `to`: the range; `path` must be a file the
  recording ran. The texts, written as [captions.md](captions.md) says: `title`, `gist`,
  `where`, `what`, `run`, and optional `why`. The page shows the title, the gist, the code, the
  step's values and `run`; `where`, `what` and `why` open with one tap.
- `call` — optional. Anchors the step to the Nth call (1-based) of the function around `from`.
  Without it, the step anchors to the first call that runs its lines. Set it when that first
  call is not the one the step is about: a function that runs for the owner and then for a
  stranger needs `"call": 2` on the stranger's step.
- `came_in`, `went_out` — optional names from the step's values. The workflow's first and last
  screens show them as what came in and what went out, with their values. The build fails on a
  name the step's values lack.
- `breakpoints` — optional; functions whose every call is a stop.

### The stop and the values

The function around `from` is the innermost recorded function whose lines hold `from`. Start a
range on a nested function's `def` to make it about that function: the enclosing function runs
that line when it makes the closure, and that run does not count.

- The step's **stop** is the first recording step of its call on the step's lines. "step
  through this" opens the debugger there, and the debugger's "next stop" lands on every step's
  stop and every breakpoint call.
- The step's **values** are its call's variables once that call has run the step's last line
  it reaches, plus the call's return value unless it is `None`. The receiver's attributes
  (`self.*`, `this.*`) are left out.

The build prints each step's anchor: the function, which call of how many, the stop, and the
call's arguments. Read them against the step's text; a wrong call shows wrong values.

## Recording — a recorder writes it

```json
{
  "version": 1,
  "language": "python",
  "entry": { "kind": "test", "target": "tests/test_upload.py::test_retry" },
  "exit": { "ok": true, "detail": "pytest exit code 0" },
  "truncated": false,
  "staging": null,
  "staged": [],
  "frames": [
    { "function": "upload.upload_file", "path": "src/upload.py",
      "start": 11, "end": 38, "parent": -1, "task": "main" }
  ],
  "steps": [[0, 12, "call", { "path": 0 }], [0, 13, "line", {}]],
  "values": ["'a.bin'"]
}
```

- `language` — `python`, `javascript` or `typescript`.
- `frames` — one per call of a watched function. `start`–`end` is the enclosing definition,
  decorators included: what the code pane shows. `parent` is the nearest watched caller's
  frame, or `-1`. `task` names the asyncio task; JS frames are all `main`.
- `steps` — `[frame, line, kind, changed]`. `kind` is one of `call line await yield resume
  return raise unwind`. `changed` maps each variable that changed since this frame's
  previous step to an index into `values`, or `-1` when it left the frame. The names
  `(return value)` and `(raised)` carry a return's value and an exception. The receiver is
  spread into one name per attribute, `self.<name>` (Python) or `this.<name>` (JS).
- `values` — every printed value once, in full, as `print` would show it. Collections still
  stop after 50 items and nesting after 4 levels.
- `truncated` — the run passed `--max-steps`; the steps stop there.
- `recorder_ms` — time the run waited for the recorder (Python only). Each frame's
  `recorder_ms` is the recorder time that passed while that call ran: any timing the code
  measured inside it is inflated by that much.
- `exact_values` — `true` with `--exact-values`: every value printed at every step. Otherwise a
  value that is still the same object with the same length is not printed again, so an
  in-place change that keeps the length shows only at the next fresh print: the return of
  the function that holds it as its own variable, or of the outermost watched call.
- `staging` — the staging folder the run imported first, relative to the root, or `null`.
  `staged` — the project paths that ran from it ([staging.md](staging.md)). Every other path
  in the recording ran from the project.
