# Sync Agent Docs

Instructions for Claude Code or Codex to sync this repo's agent config into the local
home directory. Run from the repo root. Re-runnable — only apply real differences.

Skill **content** is owned by the [`npx skills`](https://github.com/vercel-labs/skills)
CLI, which manages the shared store `~/.agents/skills/` and installs into `~/.claude`
(and other standard agents) as symlinks. `make sync` registers this repo's skills with
that CLI, then handles what the CLI can't: the docs/agents for the conventional `~/.claude`
profile and Codex. `make sync-custom` mirrors the store and syncs docs/agents into the
custom `~/.claude-sec` / `~/.claude-personal` profiles (which the CLI can't see).

## Quick run

Canned commands (no need to compose your own). `make sync` registers skills with npx,
refreshes remote skills, then syncs the conventional `~/.claude` docs/agents and Codex;
`make sync-custom` mirrors the store and syncs docs/agents into the custom profiles:

```sh
make sync           # conventional: npx skills + ~/.claude docs/agents + codex
make sync-custom    # custom profiles: mirror store + docs/agents (~/.claude-sec, ~/.claude-personal)
make sync-sec       # sync only ~/.claude-sec
make sync-personal  # sync only ~/.claude-personal
make sync-claude    # have Claude Code follow this file
make sync-codex     # have Codex follow this file
```

Each wraps the commands below.

## Commands

```sh
# 1. Register this repo's skills with the npx CLI (store + ~/.claude), non-interactive.
npx skills add ./skills --skill '*' --global --agent claude-code --yes
# 2. Refresh remote skills (mattpocock / vercel-labs) from their recorded sources.
npx skills update --global --yes
# 3. Sync conventional ~/.claude docs/agents and Codex.
python3 scripts/sync_agent_docs.py
# 4. Mirror the store and sync docs/agents into the custom profiles.
python3 scripts/sync_agent_docs.py --custom
```

For validation against a temporary home directory (python step only):

```sh
python3 scripts/sync_agent_docs.py --home /tmp/agentic-grimoire-home
```

## Sources → Targets

| Source       | Target                                    | Applies to              |
| ------------ | ----------------------------------------- | ----------------------- |
| `CLAUDE.md`  | `~/.claude/CLAUDE.md`                     | Claude                  |
| `CLAUDE.md`  | `~/.claude-sec/CLAUDE.md`                 | Claude Sec              |
| `CLAUDE.md`  | `~/.claude-personal/CLAUDE.md`            | Claude Personal         |
| `AGENTS.md`  | `~/.codex/AGENTS.md`                      | Codex                   |
| `codex/agents/*`  | `~/.codex/agents/`                   | Codex                   |
| `claude/agents/*` | `~/.claude/agents/`, `~/.claude-sec/agents/`, `~/.claude-personal/agents/` | Claude, Claude Sec, Claude Personal |
| `skills/*` (via `npx skills add`) | `~/.agents/skills/` store + `~/.claude/skills/` | Claude (npx-managed) |
| `~/.agents/skills/*` (symlinked by the script, `--custom`) | `~/.claude-sec/skills/`, `~/.claude-personal/skills/` | Claude Sec, Claude Personal |
| `.shared-agents/*`  | merged into target docs (see scope)       | varies                  |

## Task

Scope is set by the script flags: the default (`make sync`) targets the conventional
`~/.claude` profile plus Codex; `--custom` (`make sync-custom`) targets the custom
`~/.claude-sec` and `~/.claude-personal` profiles and skips Codex.

1. **Docs.** Copy `CLAUDE.md` into each in-scope Claude profile's `CLAUDE.md`
   (default: `~/.claude/`; `--custom`: `~/.claude-sec/` and `~/.claude-personal/`). On the
   default scope also copy `AGENTS.md` → `~/.codex/AGENTS.md`. Create parent dirs if missing.

2. **Shared fragments.** Merge `.shared-agents/` content inline into the target docs by scope:
   - `common/` → all generated docs
   - `claude/` → `~/.claude/CLAUDE.md` and `~/.claude-personal/CLAUDE.md`
   - `codex/`  → `~/.codex/AGENTS.md` only

   Append each fragment under a `## Shared Instructions: <relpath>` heading. Skip
   `.shared-agents/**/skills/` paths here — those are handled in step 3.

3. **Skills.** On the default scope, register this repo's `skills/` with the `npx skills`
   CLI: `npx skills add ./skills --skill '*' --global --agent claude-code --yes`. The CLI
   copies each skill into the shared store `~/.agents/skills/<name>/` and symlinks it into
   `~/.claude/skills/`. Local-path installs are not tracked in the CLI's lockfile, so
   `make sync` re-runs `add` each time to refresh them. Under `--custom`, the script mirrors
   the **whole store** into the profiles the CLI can't reach: for every
   `~/.agents/skills/<name>/`, create a relative symlink `~/.claude-sec/skills/<name>` and
   `~/.claude-personal/skills/<name>` → `../../.agents/skills/<name>`, pruning dangling store
   links and leaving real dirs / unrelated symlinks untouched.

4. **Agent definitions.** Copy each file in `claude/agents/` into each in-scope Claude
   profile's `agents/` (default: `~/.claude/agents/`; `--custom`: `~/.claude-sec/agents/`
   and `~/.claude-personal/agents/`). On the default scope also copy each file in
   `codex/agents/` → `~/.codex/agents/`.
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
