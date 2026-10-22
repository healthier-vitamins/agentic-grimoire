# Staging

The prototype branch: code that is not in the project yet runs from
`.codewalk/staging/<slug>/` and reaches the project only at Step 10.

## Write it

- Write each prototype file at its **project path** under staging, whole:
  `staging/retry/src/upload.py` replaces `src/upload.py` for the run;
  `staging/retry/src/backoff.py` adds a file the project lacks.
- The entry is a driver in `.codewalk/drivers/`. In Python, a project test also works when it
  reaches the staged code — it then runs against the staged files. vitest and jest resolve
  modules themselves, so a JS/TS prototype always runs through a driver.

## Record it

Add `--staging .codewalk/staging/<slug>` to Step 6's command. `--watch` names project paths, as
always. During the run:

- a staged file is imported in place of the project's file at the same path;
- a staged-only file imports as if it sat in the project (`from src.backoff import …`);
- every other import comes from the project, untouched.

The recording names project paths and lists the staged ones in `staged`; the page marks that
code **staged, not applied**. One page records every workflow from one staging folder.

**No project at all:** the current folder is the root and every file is staged-only — the
same flags work. At Step 10, ask the user where the code lands.

## Apply it (Step 10)

The recording's `staged` list is the file list: copy each `<staging>/<path>` to
`<project>/<path>`, then validate.
