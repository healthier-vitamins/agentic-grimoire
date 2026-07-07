# 1. Central skill store, mirrored as symlinks into every agent profile

Date: 2026-07-08

## Status

Superseded by [0002](0002-npx-skills-onboarding.md)

## Context

Skills are shared across four agent profiles: `~/.claude`, `~/.claude-sec`,
`~/.claude-personal`, and `~/.codex`. We want one canonical copy of each skill so an edit
propagates everywhere, rather than N drifting duplicates.

The [`npx skills`](https://github.com/vercel-labs/skills) CLI owns skill content. It
maintains a shared **store** at `~/.agents/skills/` (the single set of real directories) and
installs skills into agent dirs. The intended topology:

```
~/.agents/skills/   ← the store (real files)
      ▲   ▲   ▲   ▲
   .claude  -sec  -personal  .codex     ← each skills/<name> is a symlink into the store
```

Profiles point at the store, never at each other.

Two CLI behaviours complicate this:

1. **`npx add` copies local-path sources.** It symlinks github-sourced skills into agent dirs
   (default), but for a **local path** (this repo's `./skills`) it writes real-dir *copies*
   into `~/.claude/skills/` instead. Observed: remote skills (`tdd`, `wizard`) are store
   symlinks in `~/.claude`; the repo's own skills (`codewalk`, `keystone`, …) are real dirs.
2. **No store-only install.** `--agent` requires a value and `--copy` only picks
   copy-vs-symlink, so the CLI cannot be told to populate the store *without* touching an
   agent dir. The copy into `~/.claude` is unavoidable.
3. **`add` leaves the store stale.** When a local skill is already present in the store,
   `add` re-copies it into `~/.claude` but does **not** refresh the store entry. Editing a
   repo skill therefore leaves the store (and every profile that symlinks to it) behind the
   repo, while `~/.claude` gets the fresh copy — the exact drift the store was meant to kill.

Additionally, the CLI only reaches "standard" agents; it never touches the custom
`~/.claude-sec` / `~/.claude-personal` profiles, and `make sync`'s `--agent claude-code` run
never touches `~/.codex/skills`.

## Decision

`scripts/sync_agent_docs.py` owns the store's local-skill content and the symlink topology
for **all four** profiles. After `npx add` runs, the script first **refreshes the store from
the repo** — `skills/` is the source of truth for this repo's own skills, so each store entry
is overwritten when it differs (remote / store-only skills are left to `npx update`). It then
mirrors the whole store into every in-scope profile via relative symlinks
(`<profile>/skills/<name>` → `../../.agents/skills/<name>`):

- **Relink identical copies.** If a target is a real dir whose content is **identical** to the
  store skill (an npx copy), delete it and replace with the store symlink.
- **Preserve divergence.** If a real dir **differs** from the store skill, leave it in place
  and warn. The script never destroys content it did not create. (Live example at adoption:
  `~/.claude/skills/ui-ux-pro-max` diverged from the store and was preserved.)
- **Leave the rest alone.** Skills absent from the store (e.g. `context7-mcp`, personal-only
  dirs) and unrelated symlinks are untouched; dangling store links are pruned.

Codex receives the whole store too. Symlinking is inert — codex discovers skills by
`SKILL.md`, and hooks only run when explicitly wired in `config.toml`, so no skill activates
merely by being linked. Claude-specific skills simply sit unused there.

## Consequences

- One real copy of each skill in the store; every profile is a symlink into it, so edits
  propagate everywhere. This matches what the remote skills already did.
- `make sync` is self-healing: `npx add` re-copies local skills into `~/.claude` each run, and
  the script relinks them in the same invocation. Idempotent once settled.
- A skill that diverges from the store in a profile stays a real-dir copy (one exception to
  full symlink parity) until reconciled by hand — a deliberate safety trade to avoid silent
  data loss.
- The sync fights the CLI's copy behaviour rather than avoiding it, because no store-only
  install flag exists. If the CLI later adds one, the relink step can be dropped.
