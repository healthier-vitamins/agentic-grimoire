# agentic-grimoire

Managed agent instruction files and skills for Codex and Claude. An agent (Claude Code or Codex) syncs them into the local home directory by following `SYNC.md`.

## What This Repo Does

This repo keeps two source instruction files:

- `.claude/CLAUDE.md`
- `.codex/AGENTS.md`

Plus shared fragments under `.shared-agents/` and skills under `skills/`. Syncing copies these into the expected locations in the current user's home directory.

## Sync

There is no installer script. Hand `SYNC.md` to Claude Code or Codex from the repo root and let it run the sync:

```text
Follow SYNC.md
```

`SYNC.md` writes or updates these targets under the current user's home directory:

- `~/.claude/CLAUDE.md`
- `~/.codex/AGENTS.md`
- `~/.claude/skills/` and `~/.codex/skills/`

The sync is idempotent: targets that already match are left unchanged, unrelated existing content in the home files is preserved, and conflicting symlinks are left in place with a warning.

## Shared Content

If a `.shared-agents/` directory exists in the repo, the installer merges those instruction files into the generated docs.

If a root `skills/` directory exists, the installer copies each skill into both `~/.claude/skills/` and `~/.codex/skills/`.

Scope rules:

- `common/` content applies to both agents
- `claude/` content applies only to `CLAUDE.md`
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
3. Hand `SYNC.md` to Claude Code or Codex from the repo root.
4. Review the per-target statuses it prints to confirm what changed.
