---
name: watermark
description: Create logical, atomic Conventional Commits from the current uncommitted work, in the repo's commit style. Never pushes.
disable-model-invocation: true
---

Goal: turn the current uncommitted work into a set of clean, atomic Conventional Commits.

This skill is user-invoked only. Read `commit-format.md` (same directory) before composing any message — it holds the Conventional Commit rules and the exact commit command.

## Identity (governs the commit message)

The single source of truth for identity, signing, and trailers — `commit-format.md` and every step point here:

- Author identity and any GPG signature come from the user's normal git config (`%an`/`%ae` and the signature are expected — nothing overridden).
- Claude's default `Co-Authored-By: Claude` trailer stays. Fabricate no session id/URL trailers.
- Keep the user's personal name/email out of the subject, body, and trailers.

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

Decide what is in scope; **do not stage yet** — staging happens in Step 5, one concern at a time, driven by the Step 4 concern table.

- Files whose entire diff belongs to one concern → whole-file staging later.
- A file that holds two concerns → split it non-interactively (see Step 5); do **not** rely on interactive `git add -p`, an agent can't drive its TTY reliably.
- Leave unrelated or uncertain changes unstaged.

**Criterion:** every current change is either assigned to a concern or explicitly left out with a reason. If there are no commit-worthy changes, say so and stop.

## Step 3 — Safety gates (abort with a clear message on any failure)

- **Branch:** commit on the current branch — including `main`/`master`; nothing is ever pushed, so local commits there are safe. Only if the user explicitly asked for a new branch or new worktree, create it first and commit there; otherwise never switch branches.
- **Secrets/artifacts:** refuse to stage `.env`, key material, credentials, or build output. Warn and exclude.

**Criterion:** on the branch the user intends (current branch by default), no secrets staged.

## Step 4 — Decompose into atomic commits (do this BEFORE staging)

This is the step that keeps commits granular. It runs automatically — there is no human preview, so the verification pass below is the only check.

**Emit a concern table first.** Before any `git add`, output a table covering the whole diff:

| concern | files / hunks | type(scope) | why (one line) |
|---|---|---|---|

Rules for the table:

- **Always-split triggers (fire regardless of how "one concern" it feels):**
  - New files (scaffold) vs. edits that wire them in → separate rows.
  - Tests vs. the implementation they cover → separate rows.
  - Docs/config vs. code → separate rows.
  - A row touching more than a handful of files, or mixing new **and** modified files → stop and justify inline (see verification) why it is genuinely atomic; if you can't, split it.
- **The "and" test:** if a row's *why* needs the word "and", it is two concerns — split the row. One logical change per commit.
- **Logical unit, not file count:** a single concern spans as many files as it needs; do not split one change across per-file commits. A rename plus its import updates is **one** row. **But when this rule and "bias to split" conflict, split wins** — this rule only prevents per-file over-splitting, it never licenses a fat catch-all commit.
- **Never merge unrelated types:** a `feat` and an unrelated `fix` are always separate rows, even if small.
- **Bias to split:** when unsure whether two changes are one concern or two, make them two rows.
- **Sweep-back check:** every path in `git status --short` must appear in at least one row, or be explicitly excluded per Step 1. A missing path means a concern was lumped or dropped — regenerate the table.
- **Order rows so dependencies land first:** a refactor/chore that later commits build on comes before the `feat` that uses it, so every commit leaves the tree building (build-green invariant).

**Large diff (many files / hunks):** analyze each changed file's diff separately, note its concern(s), then cluster into the table — one pass over a big diff invites truncation and lumping.

**Verification pass (do this after the table, before staging):** re-read the diff once against the table. For every row with more than one file, or a new+modified mix, write a one-line atomicity justification in the *why* column ("atomic: X because Y"). A row you cannot justify in one line fails an always-split trigger — split it and regenerate the table.

**Criterion:** the table is emitted before staging; every changed path maps to exactly one row (or is excluded with a reason); each row passes the "and" test and every always-split trigger; multi-file / new+modified rows carry an inline atomicity justification.

## Step 5 — Compose and commit each group (auto, no preview)

For each row of the Step 4 table, in order:
1. Stage exactly that row's files/hunks.
   - Whole-file: `git add <file>`.
   - One file, two concerns: build the patch non-interactively — `git diff -- <file>` → keep only the target hunks → `git apply --cached <patch>`. Commit, then stage and commit the remainder as its own row.
2. Compose a Conventional Commit message per `commit-format.md` — subject line, then the point-form body shape and its cut.
3. Commit with the plain `git commit` in `commit-format.md`; identity, signing, and trailers follow the Identity section above.

**Criterion:** one commit per row; each commit touches only its concern (no commit mixes unrelated concerns); every message matches `commit-format.md` — imperative subject, and where a body is present, one lead line plus one-idea bullets; unrelated work remains unstaged; **nothing pushed**.

## Step 6 — Report

List the commits created (hashes + subjects), echo the Step 4 concern table so the grouping is auditable, and note any files intentionally left uncommitted. Confirm nothing was pushed. The report text follows the Identity rule too — no personal name/email.
