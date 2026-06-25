# agentic-grimoire

Managed agent instruction files and skills for Codex, Claude, and Claude Personal. An agent (Claude Code or Codex) syncs them into the local home directory by following `SYNC.md`.

> _Running a sync resets any old-syntax managed blocks in your home files to the current format._

## What This Repo Does

This repo keeps two source instruction files:

- `.claude/CLAUDE.md`
- `.codex/AGENTS.md`

Plus shared fragments under `.shared-agents/` and skills under `skills/`. Syncing copies these into the expected locations in the current user's home directory.

## Sync

Syncing is agent-driven: follow [`SYNC.md`](SYNC.md) from the repo root — the canonical, re-runnable procedure for both agents. From a terminal, use the canned commands:

```sh
make sync         # run the sync directly
make sync-claude  # have Claude Code follow SYNC.md
make sync-codex   # have Codex follow SYNC.md
```

`SYNC.md` writes or updates these targets under the current user's home directory:

- `~/.claude/CLAUDE.md`
- `~/.claude-personal/CLAUDE.md`
- `~/.codex/AGENTS.md`
- `~/.claude/skills/`, `~/.claude-personal/skills/`, and `~/.codex/skills/`

The sync is idempotent: targets that already match are left unchanged, unrelated existing content in the home files is preserved outside the managed block, and conflicting symlinks are left in place with a warning.

## Shared Content

If a `.shared-agents/` directory exists in the repo, the installer merges those instruction files into the generated docs.

If a root `skills/` directory exists, the installer copies each skill into `~/.claude/skills/`, `~/.claude-personal/skills/`, and `~/.codex/skills/`.

Scope rules:

- `common/` content applies to all generated docs
- `claude/` content applies to both Claude `CLAUDE.md` files
- `codex/` content applies only to `AGENTS.md`

## Repo Layout

Key paths:

- `SYNC.md` - sync instructions an agent follows
- `.claude/CLAUDE.md` - Claude source instructions
- `.codex/AGENTS.md` - Codex source instructions
- `.shared-agents/` - optional shared instruction fragments merged during sync
- `skills/` - skills synced for both agents

## Typical Workflow

1. Edit the source docs in `.claude/` or `.codex/`.
2. Optionally add shared fragments under `.shared-agents/` or skills under `skills/`.
3. Sync by following [`SYNC.md`](SYNC.md) — e.g. `make sync` (or `make sync-claude` / `make sync-codex`).
4. Review the per-target statuses it prints to confirm what changed.
