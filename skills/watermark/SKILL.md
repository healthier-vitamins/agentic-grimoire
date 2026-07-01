---
name: watermark
description: Commit only the changes made during this session — grouped into logical, atomic Conventional Commits — and leave pre-existing uncommitted work untouched. Never pushes. Use when the user says "watermark", "commit this session", or wants session-scoped logical commits.
disable-model-invocation: true
---

Goal: turn everything you changed **during this session** into a set of clean, atomic Conventional Commits, while ignoring any dirty state that existed before the session started. The session baseline is the **high-water mark**; watermark commits everything above it and nothing below.

This skill is user-invoked only. Read `commit-format.md` (same directory) before composing any message — it holds the Conventional Commit rules and the exact commit command.

## Privacy invariant (governs the commit message)

Commit with the user's normal git identity and signing — the `%an`/`%ae` author fields and any GPG signature come from their git config and are expected. The one thing to guard is the commit **message**: never inject the session id/URL or the user's personal name/email into the subject, body, or trailers. The only trailer is the assistant's `noreply` co-author line (no `Claude-Session` line).

## Step 1 — Locate the watermark

Read the baseline marker for this session, written by the SessionStart hook:

```sh
git rev-parse --git-dir   # → <git-dir>
# baseline file: <git-dir>/watermark-<session_id>.baseline
```

The file holds a single git ref (a stash-style commit if the tree was dirty at session start, else the HEAD sha). Resolve it. A sibling marker `<git-dir>/watermark-<session_id>.untracked` lists the files that were already untracked at session start (`git stash create` cannot capture those) — read it too.

**Criterion:** a baseline ref is resolved. If the marker is missing or the ref does not resolve, **stop and report** — do not guess a baseline (guessing risks committing pre-session work).

## Step 2 — Compute session-scoped changes

Diff the working tree against the baseline to find what this session touched:

```sh
git diff --name-status <baseline>          # tracked changes since baseline
git ls-files --others --exclude-standard   # currently-untracked files
```

Untracked session adds = currently-untracked files **minus** the paths listed in the `.untracked` baseline marker (those pre-date the session — ignore them).

For each path:
- **Clean at the watermark** (unchanged in the baseline) → stage the whole file.
- **Already dirty at the watermark** → isolate only the session hunks (the delta between the baseline and the current file) and stage just those:

  ```sh
  git diff <baseline> -- <file> | git apply --cached --3way
  ```

  When the session hunks are disjoint from the pre-session edits this stages the session changes on top of `HEAD`, leaving the pre-session edits uncommitted in the working tree. If `--3way` cannot apply cleanly (session and pre-session edits overlap), **surface that file for manual handling** rather than staging pre-session content.

**Criterion:** every session-scoped path is accounted for — staged, or explicitly surfaced for manual handling. Nothing excluded silently. If there are no session changes, say so and stop.

## Step 3 — Safety gates (abort with a clear message on any failure)

- **Branch:** if on the default branch (`main`/`master`), create a feature branch first and commit there. Never commit session work directly onto the default branch.
- **Secrets/artifacts:** refuse to stage `.env`, key material, credentials, or build output. Warn and exclude.
- **Validation:** run the project's validation (lint / typecheck / test) per `./.shared-agents/common/linting.md`. Abort before committing if it fails.

**Criterion:** branch is safe, no secrets staged, validation green.

## Step 4 — Group into atomic commits

Group the staged changes by **concern/feature**, not by file type. Order groups so dependencies land first (a refactor or chore that later commits build on comes before the `feat` that uses it).

**Criterion:** every staged change belongs to exactly one group.

## Step 5 — Compose and commit each group (auto, no preview)

For each group, in dependency order:
1. Stage exactly that group's changes.
2. Compose a Conventional Commit message per `commit-format.md` (terse, imperative, why-over-what).
3. Commit with the user's normal git identity and signing (the plain `git commit` in `commit-format.md`), adding the assistant's `Co-Authored-By` trailer. Keep the session id/URL and personal name/email out of the message.

**Criterion:** one commit per group; everything above the watermark committed; **nothing pushed**.

## Step 6 — Report

List the commits created (hashes + subjects) and any files surfaced for manual handling. Confirm nothing was pushed. Honor the Privacy invariant in the report text.
