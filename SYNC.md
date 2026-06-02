# Sync Agent Docs

Instructions for Claude Code or Codex to sync this repo's agent config into the local
home directory. Run from the repo root. Re-runnable — only apply real differences.

## Sources → Targets

| Source              | Target                                    | Applies to |
| ------------------- | ----------------------------------------- | ---------- |
| `.claude/CLAUDE.md` | `~/.claude/CLAUDE.md`                     | Claude     |
| `.codex/AGENTS.md`  | `~/.codex/AGENTS.md`                      | Codex      |
| `skills/*`          | `~/.claude/skills/` + `~/.codex/skills/`  | both       |
| `.shared-agents/*`  | merged into target docs (see scope)       | varies     |

## Task

1. **Docs.** Copy `.claude/CLAUDE.md` → `~/.claude/CLAUDE.md` and `.codex/AGENTS.md`
   → `~/.codex/AGENTS.md`. Create parent dirs if missing.

2. **Shared fragments.** Merge `.shared-agents/` content inline into the target docs by scope:
   - `common/` → both `~/.claude/CLAUDE.md` and `~/.codex/AGENTS.md`
   - `claude/` → `~/.claude/CLAUDE.md` only
   - `codex/`  → `~/.codex/AGENTS.md` only

   Append each fragment under a `## Shared Instructions: <relpath>` heading. Skip
   `.shared-agents/**/skills/` paths here — those are handled in step 3.

3. **Skills.** Copy every `skills/<name>/` directory into both `~/.claude/skills/<name>/`
   and `~/.codex/skills/<name>/`, preserving files. Each skill must keep its leading YAML
   frontmatter in `SKILL.md`; skip any `SKILL.md` missing frontmatter and warn.

## Rules

- Idempotent: if a target already matches, leave it unchanged.
- Preserve unrelated existing content in the home files — do not clobber the user's own
  notes; merge changes in place.
- Print a short per-target status: created / updated / unchanged / skipped.
- If a target is a symlink to an unmanaged file, leave it and warn.
