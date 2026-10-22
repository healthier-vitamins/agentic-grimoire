# Page format

The two files `build.py` joins into the page, one pair per workflow, paired by file name:
`.codewalk/walkthrough/<workflow>.json` and `.codewalk/recordings/<workflow>.json`. The page
lists workflows in file-name order, so name them `01-checkout`, `02-refund` to keep the
confirmed map's order. Every path is relative to the project root, with `/` separators.
Lines are 1-based.

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
  "steps": [
    { "path": "src/upload.py", "from": 12, "to": 18, "caption": "Why these lines exist." }
  ],
  "breakpoints": ["upload._send_chunk"]
}
```

- `functions` — the map the user confirmed, in call order. `name` is `module.qualname`, the
  same form a recording's frames use.
- `fakes` — one line per faked call: what, and why. Empty when every call ran for real.
- `steps` — the walkthrough, in reading order. Each `path` must be a file the recording ran;
  the build fails otherwise. The debugger's "next stop" lands on the first step that runs a
  walkthrough step's lines.
- `breakpoints` — optional; functions whose every call is a stop.

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
  `(return value)` and `(raised)` carry a return's value and an exception.
- `values` — every printed value once, as `print` would show it, cut at 4000 characters.
- `truncated` — the run passed `--max-steps`; the steps stop there.
- `staging` — the staging folder the run imported first, relative to the root, or `null`.
  `staged` — the project paths that ran from it ([staging.md](staging.md)). Every other path
  in the recording ran from the project.
