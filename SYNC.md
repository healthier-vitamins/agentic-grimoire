# Sync Agent Docs

Instructions for Claude Code or Codex to sync this repo's agent config into the local
home directory. Run from the repo root. Re-runnable — only apply real differences.

## Quick run

Canned commands (no need to compose your own) — all update `~/.claude`,
`~/.claude-personal`, and `~/.codex` in one go:

```sh
make sync         # run the sync directly
make sync-claude  # have Claude Code follow this file
make sync-codex   # have Codex follow this file
```

Each wraps the command below.

## Command

```sh
python3 scripts/sync_agent_docs.py
```

For validation against a temporary home directory:

```sh
python3 scripts/sync_agent_docs.py --home /tmp/agentic-grimoire-home
```

## Sources → Targets

| Source       | Target                                    | Applies to              |
| ------------ | ----------------------------------------- | ----------------------- |
| `CLAUDE.md`  | `~/.claude/CLAUDE.md`                     | Claude                  |
| `CLAUDE.md`  | `~/.claude-personal/CLAUDE.md`            | Claude Personal         |
| `AGENTS.md`  | `~/.codex/AGENTS.md`                      | Codex                   |
| `codex/agents/*`  | `~/.codex/agents/`                   | Codex                   |
| `claude/agents/*` | `~/.claude/agents/`, `~/.claude-personal/agents/` | Claude, Claude Personal |
| `skills/*`   | all configured `skills/` target dirs      | Claude, Claude Personal, Codex |
| `.shared-agents/*`  | merged into target docs (see scope)       | varies                  |

## Task

1. **Docs.** Copy `CLAUDE.md` → `~/.claude/CLAUDE.md` and
   `~/.claude-personal/CLAUDE.md`; copy `AGENTS.md` →
   `~/.codex/AGENTS.md`. Create parent dirs if missing.

2. **Shared fragments.** Merge `.shared-agents/` content inline into the target docs by scope:
   - `common/` → all generated docs
   - `claude/` → `~/.claude/CLAUDE.md` and `~/.claude-personal/CLAUDE.md`
   - `codex/`  → `~/.codex/AGENTS.md` only

   Append each fragment under a `## Shared Instructions: <relpath>` heading. Skip
   `.shared-agents/**/skills/` paths here — those are handled in step 3.

3. **Skills.** Copy every `skills/<name>/` directory into
   `~/.claude/skills/<name>/`, `~/.claude-personal/skills/<name>/`, and
   `~/.agents/skills/<name>/`, preserving files. Each skill must keep its leading
   YAML frontmatter in `SKILL.md`; skip any `SKILL.md` missing frontmatter and warn.

4. **Agent definitions.** Copy each file in `codex/agents/` → `~/.codex/agents/`, and
   each file in `claude/agents/` → `~/.claude/agents/` and `~/.claude-personal/agents/`.
   Create parent dirs if missing; leave a target that already matches unchanged; skip an
   unmanaged symlink with a warning.

## Rules

- Idempotent: if a target already matches, leave it unchanged.
- Preserve unrelated existing content in the home files — do not clobber the user's own
  notes; merge changes in place.
- Rewrite any managed block that isn't in the current
  `<!-- AGENTIC-GRIMOIRE: MANAGED FILE -->` format into it; do not preserve old
  generated block contents (only user content outside the managed block survives).
- Print a short per-target status: created / updated / unchanged / skipped.
- If a target is a symlink to an unmanaged file, leave it and warn.
