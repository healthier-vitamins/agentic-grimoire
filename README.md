# agentic-grimoire

Managed agent instruction files and skills for Codex, Claude, and Claude Personal. An agent (Claude Code or Codex) syncs them into the local home directory by following `SYNC.md`.

> _Running a sync resets any old-syntax managed blocks in your home files to the current format._

## What This Repo Does

This repo keeps two source instruction files:

- `CLAUDE.md`
- `AGENTS.md`

Plus shared fragments under `.shared-agents/` and skills under `skills/`. Syncing copies these into the expected locations in the current user's home directory.

## Sync

Syncing is agent-driven: follow [`SYNC.md`](SYNC.md) from the repo root — the canonical, re-runnable procedure for both agents. From a terminal, use the canned commands:

```sh
make sync         # conventional: skills + ~/.claude docs/agents + codex
make sync-custom  # custom profiles: ~/.claude-sec and ~/.claude-personal
make sync-claude  # have Claude Code follow SYNC.md
make sync-codex   # have Codex follow SYNC.md
```

`make sync` writes or updates the **conventional** targets under the current user's home directory:

- `~/.claude/CLAUDE.md`
- `~/.codex/AGENTS.md`
- `~/.claude/agents/` (from `claude/agents/`) and `~/.codex/agents/` (from `codex/agents/`)
- `~/.agents/skills/` (the store, via the `npx skills` CLI) mirrored as symlinks into `~/.claude/skills/` and `~/.codex/skills/`

`make sync-custom` writes the **unconventional** profiles the npx CLI can't see (run `make sync` first to populate the store):

- `~/.claude-sec/CLAUDE.md` and `~/.claude-personal/CLAUDE.md`
- `~/.claude-sec/agents/` and `~/.claude-personal/agents/` (from `claude/agents/`)
- `~/.claude-sec/skills/` and `~/.claude-personal/skills/` (symlink mirror of `~/.agents/skills/`)

The sync is idempotent: targets that already match are left unchanged, unrelated existing content in the home files is preserved outside the managed block, and conflicting symlinks are left in place with a warning.

## Shared Content

If a `.shared-agents/` directory exists in the repo, the installer merges those instruction files into the generated docs.

If a root `skills/` directory exists, the `npx skills` CLI registers each skill into the shared store `~/.agents/skills/`. `npx add` symlinks github-sourced skills into `~/.claude/skills/` but *copies* local-path sources (this repo's `skills/`) there, and leaves an already-present store entry stale. So the sync script first **refreshes the store from the repo** (the repo's `skills/` is the source of truth for its own skills), then relinks the content-identical copies into store symlinks and mirrors the store into `~/.codex/skills/`. `make sync-custom` mirrors the store into `~/.claude-sec/skills/` and `~/.claude-personal/skills/`. Every profile ends up with symlinks into the one store; a real dir that differs from the store is left in place with a warning.

Scope rules:

- `common/` content applies to all generated docs
- `claude/` content applies to both Claude `CLAUDE.md` files
- `codex/` content applies only to `AGENTS.md`

## Repo Layout

Key paths:

- `SYNC.md` - sync instructions an agent follows
- `CLAUDE.md` - Claude source instructions
- `AGENTS.md` - Codex source instructions
- `.shared-agents/` - optional shared instruction fragments merged during sync
- `codex/agents/` - Codex subagent definitions synced to `~/.codex/agents/`
- `claude/agents/` - Claude subagent definitions synced to `~/.claude/agents/` and `~/.claude-personal/agents/`
- `skills/` - skills synced for both agents

## Typical Workflow

1. Edit the source docs `CLAUDE.md` or `AGENTS.md` at the repo root.
2. Optionally add shared fragments under `.shared-agents/` or skills under `skills/`.
3. Sync by following [`SYNC.md`](SYNC.md) — e.g. `make sync` (or `make sync-claude` / `make sync-codex`).
4. Review the per-target statuses it prints to confirm what changed.
