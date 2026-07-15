---
name: link-agentic-grimoire-custom
description: Mirror root ~/.claude's config into the custom Claude profiles ~/.claude-personal and ~/.claude-sec — relative-symlink CLAUDE.md, RTK.md, rules, skills, agents, and commands to root so they never drift. Run after /setup-agentic-grimoire.
disable-model-invocation: true
---

Root `~/.claude` is the single source of truth for config. The custom profiles are separate
*accounts* (selected by `CLAUDE_CONFIG_DIR`), not separate setups, so their **config** should
mirror root instead of drifting. This skill relative-symlinks root's config allowlist into each.

Prerequisite: `/setup-agentic-grimoire` has run against root — it populates root's `skills/`
(a symlink farm over the `~/.agents/skills` store) and splices root's `CLAUDE.md`. The custom
profiles inherit both simply by mirroring root.

Let `DIR` be this skill's own directory.

## What gets linked (allowlist) vs left alone

| Item | Action |
|---|---|
| `CLAUDE.md`, `RTK.md`, `rules/`, `skills/`, `agents/`, `commands/` | symlink → root |
| `.claude.json` + Keychain auth | **never touched** — this is the account identity |
| `settings.json`, `projects/` (chats + memory), `plans/`, `history.jsonl`, caches, runtime | **never touched** — per-profile / knowledge |

`skills/` is a single dir symlink to root's `skills/`, so each profile inherits root's whole
skill set — the `~/.agents/skills` store *and* any root-local skills — through one link.
The script only ever acts on that fixed allowlist; a denylist assertion refuses account,
settings, and knowledge items even if a future edit lists them.

## Steps

1. **Dry-run first** (changes nothing — read the full action list):
   ```sh
   bash "$DIR/link.sh" --dry-run
   ```
   Confirm no `.claude.json`/`settings.json` and no `projects`/`plans`/`history.jsonl` appear.

2. **Link:**
   ```sh
   bash "$DIR/link.sh"          # defaults to .claude-personal and .claude-sec
   ```

3. **Report** per profile: which items `link`ed / were `backup`ed / are `ok` (already linked).
   Confirm each `.claude.json` is untouched and still shows its own account.

Override the source with `--target DIR` or pass explicit profile names as arguments.

## Safety

- Relative symlinks; a real file/dir is moved to `<profile>/backups/<item>-<ts>` before it is
  replaced — nothing is deleted.
- Idempotent: re-running skips anything already linked to root.
- Never symlinks `.claude.json` or Keychain auth, so the custom accounts stay distinct.

## Relationship to other skills

- **Composes with `setup-agentic-grimoire`**, which populates *root*; this skill then
  propagates root's config to the custom profiles.

**Criterion:** each custom profile's six config items resolve into `~/.claude`; `.claude.json`,
settings, and knowledge (`projects/`, `plans/`, `history.jsonl`) are untouched; a second run is
idempotent; every replaced original survives under `<profile>/backups/`.
