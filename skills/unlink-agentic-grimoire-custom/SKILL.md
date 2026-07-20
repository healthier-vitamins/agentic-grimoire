---
name: unlink-agentic-grimoire-custom
description: Reverse /link-agentic-grimoire-custom — remove the config symlinks (CLAUDE.md, rules, skills, agents, commands) that mirror root into ~/.claude-personal and ~/.claude-sec, restoring each profile's own file from backups so it stops mirroring root. Never touches account, settings, or knowledge.
disable-model-invocation: true
---

The exact inverse of `link-agentic-grimoire-custom`. That skill relative-symlinks root's config
allowlist into each custom profile so their config mirrors root; this one removes those symlinks
and restores whatever real file/dir `link.sh` backed up, so each profile owns its config again.

Use this to make a custom profile *independent* of root. It is **separate from**
`uninstall-agentic-grimoire`, which only de-manages root (strips the guideline block and removes
this repo's skills). Full teardown of a linked setup is `uninstall` + `unlink`.

Let `DIR` be this skill's own directory.

## What gets unlinked (allowlist) vs left alone

| Item | Action |
|---|---|
| `CLAUDE.md`, `rules/`, `skills/`, `agents/`, `commands/` | remove symlink → restore from `backups/` if present |
| `.claude.json` + Keychain auth | **never touched** — this is the account identity |
| `settings.json`, `projects/` (chats + memory), `plans/`, `history.jsonl`, caches, runtime | **never touched** — per-profile / knowledge |

Only a symlink whose value **equals** what `link.sh` would have created (i.e. points into root)
is removed; a real file/dir or a foreign symlink is left untouched. The same denylist assertion
as `link.sh` refuses account, settings, and knowledge items even if a future edit lists them.

## Steps

1. **Dry-run first** (changes nothing — read the full action list):
   ```sh
   bash "$DIR/unlink.sh" --dry-run
   ```
   Confirm no `.claude.json`/`settings.json` and no `projects`/`plans`/`history.jsonl` appear,
   and that every planned `rm`/`restore` targets only a root-pointing config symlink.

2. **Unlink:**
   ```sh
   bash "$DIR/unlink.sh"          # defaults to .claude-personal and .claude-sec
   ```

3. **Report** per profile: which items were `restore`d from `backups/`, which were `unlink`ed
   with no backup, and which were `skip`ped (real file, foreign link, or absent). Confirm each
   `.claude.json` is untouched and still shows its own account.

Override the source with `--target DIR` or pass explicit profile names as arguments.

## Safety

- Removes only symlinks that point into root exactly as `link.sh` wrote them; real files/dirs and
  foreign symlinks are skipped, never deleted.
- Restores the most-recent `backups/<item>-<ts>` via `mv` (consuming that backup); if none exists
  the item is simply removed (it never had a real original — e.g. a fresh profile).
- Idempotent: re-running finds real files / absent items and skips.
- Never touches `.claude.json` or Keychain auth, so the custom accounts stay distinct.

## Relationship to other skills

- **Inverse of `link-agentic-grimoire-custom`** — same allowlist, denylist, and relative-symlink
  convention, run in reverse.
- **Distinct from `uninstall-agentic-grimoire`**, which owns only root's guideline block and this
  repo's skills. `unlink` never de-manages root.

**Criterion:** each custom profile's six config items are restored from `backups/` or absent — no
root-pointing config symlink remains; `.claude.json`, settings, and knowledge (`projects/`,
`plans/`, `history.jsonl`) are untouched; a second run is idempotent (all `skip`).
