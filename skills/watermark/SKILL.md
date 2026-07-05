---
name: watermark
description: Create logical, atomic Conventional Commits from the current uncommitted work, following the repository's commit style. Never pushes. Use when the user says "watermark", "commit this", or asks for logical commits.
disable-model-invocation: true
---

Goal: turn the current uncommitted work into a set of clean, atomic Conventional Commits.

This skill is user-invoked only. Read `commit-format.md` (same directory) before composing any message — it holds the Conventional Commit rules and the exact commit command.

## Identity (governs the commit message)

Commit with the user's normal git identity and signing — the `%an`/`%ae` author fields and any GPG signature come from their git config and are expected. Claude's default `Co-Authored-By: Claude` trailer is fine; leave it. Keep the user's personal name/email out of the subject, body, or trailers.

## Step 1 — Inspect the worktree

Inspect the current uncommitted state and recent commit style:

```sh
git status --short
git diff --stat
git diff
git log --oneline -5
```

**Criterion:** every changed path is understood. If the worktree contains changes that look unrelated to the user's request or may pre-date the current work, surface them and exclude them unless the user explicitly includes them.

## Step 2 — Choose commit scope

Stage only the changes that belong in the requested commits:

- Use whole-file staging for files whose entire diff belongs to one commit.
- Use hunk staging when a file contains multiple logical changes.
- Leave unrelated or uncertain changes unstaged.

**Criterion:** every current change is either staged for a specific commit or explicitly left out with a reason. If there are no commit-worthy changes, say so and stop.

## Step 3 — Safety gates (abort with a clear message on any failure)

- **Branch:** if on the default branch (`main`/`master`), create a feature branch first and commit there. Never commit session work directly onto the default branch.
- **Secrets/artifacts:** refuse to stage `.env`, key material, credentials, or build output. Warn and exclude.

**Criterion:** branch is safe, no secrets staged.

## Step 4 — Group into atomic commits

Group the staged changes by **concern/feature**, not by file type. Order groups so dependencies land first (a refactor or chore that later commits build on comes before the `feat` that uses it).

**Criterion:** every staged change belongs to exactly one group.

## Step 5 — Compose and commit each group (auto, no preview)

For each group, in dependency order:
1. Stage exactly that group's changes.
2. Compose a Conventional Commit message per `commit-format.md` (terse, imperative, why-over-what).
3. Commit with the user's normal git identity and signing (the plain `git commit` in `commit-format.md`). Claude's default co-author trailer is fine; keep the user's personal name/email out of the message.

**Criterion:** one commit per group; requested work committed; unrelated work remains unstaged; **nothing pushed**.

## Step 6 — Report

List the commits created (hashes + subjects) and any files intentionally left uncommitted. Confirm nothing was pushed. Keep the user's personal name/email out of the report text.
