---
name: uninstall-agentic-grimoire
description: Fully remove agentic-grimoire — strip the guideline block from all profiles' memory files and remove this repo's skills from the store and every profile. Leaves other sources' skills untouched.
disable-model-invocation: true
---

## Scope boundary (hard rule)

This uninstaller removes **only what this repo published** — the skill directories listed in
`$SKILLS` (read live from the lockfile by source, see Steps) plus the managed
`CLAUDE.md` / `AGENTS.md` block. Skills installed from any other source are **left installed**.
Never run `npx skills remove --all`.

## How it works

- `unsplice.sh` (this directory) is the deterministic inverse of `setup-agentic-grimoire`'s
  `splice.sh`: it removes only the region between `<!-- AGENTIC-GRIMOIRE: MANAGED FILE -->` …
  `<!-- END AGENTIC-GRIMOIRE: MANAGED FILE -->` (and the `USER CONTENT` marker line),
  preserving everything the user wrote outside it. No-op on a file without the markers.
- `npx skills remove` removes the store copy and the conventional-profile symlinks. It removes
  **by skill name**, so we pass exactly the names installed from this source, read live from
  `~/.agents/.skill-lock.json` (drift-proof, and it catches stale installs a hardcoded list would miss).
- Removing the store dirs can leave *legacy* per-skill symlinks (the old symlink-farm layout)
  dangling in a custom profile; a prune of dead store links finishes the job. Profiles on the
  current layout (a single `skills/` dir symlink to root, plus the other config symlinks) are
  reversed by `/unlink-agentic-grimoire-custom`, not here — this uninstaller only de-manages root.

## Steps

Let `DIR` be this skill's own directory (the folder holding this `SKILL.md`, i.e.
`~/.agents/skills/uninstall-agentic-grimoire`).

The skills to remove — exactly those installed from this source, read from the lockfile so the
list can never drift and always includes stale installs (skills deleted from the repo but still
on this machine):

```sh
SKILLS="$(jq -r '.skills // {} | to_entries[]
  | select(.value.source == "healthier-vitamins/agentic-grimoire") | .key' \
  "$HOME/.agents/.skill-lock.json" 2>/dev/null | tr '\n' ' ')"
```

1. **Preview the block removal.** Unsplice into throwaway copies and diff, so the user sees
   exactly what leaves each memory file before any real write:
   ```sh
   for f in "$HOME/.claude/CLAUDE.md" "$HOME/.codex/AGENTS.md" \
            "$HOME/.claude-personal/CLAUDE.md" "$HOME/.claude-sec/CLAUDE.md"; do
     [ -e "$f" ] || continue
     [ -L "$f" ] && continue   # symlink -> root; root's own entry already covers it
     tmp="$(mktemp)"; cp "$f" "$tmp"
     bash "$DIR/unsplice.sh" "$tmp" >/dev/null
     echo "=== $f ==="; diff -u "$f" "$tmp" 2>/dev/null || true; rm -f "$tmp"
   done
   ```

2. **Strip the guideline block** from all four profiles' memory files. Do this **before**
   step 3 — `npx skills remove` deletes this skill (and `unsplice.sh`) from the store:
   ```sh
   for f in "$HOME/.claude/CLAUDE.md" "$HOME/.codex/AGENTS.md" \
            "$HOME/.claude-personal/CLAUDE.md" "$HOME/.claude-sec/CLAUDE.md"; do
     [ -L "$f" ] && continue   # symlink -> root; root's own entry already covers it
     [ -e "$f" ] && bash "$DIR/unsplice.sh" "$f"
   done
   ```
   Each prints `updated` / `unchanged`. A profile `CLAUDE.md` that symlinks to root is skipped
   here — root's single strip covers it; a legacy real-file profile (pre-link) is stripped in place.

3. **Remove this repo's skills** from the store and the conventional profiles (skip if the
   lockfile listed none — nothing was installed from this source):
   ```sh
   [ -n "${SKILLS// /}" ] && npx skills remove --global -a claude-code codex --yes $SKILLS
   ```
   Only the names in `$SKILLS` are removed. Other sources' skills are untouched.

4. **Prune dangling *legacy* per-skill symlinks** (old symlink-farm layout only; removes dead
   links that point into the store — never a real dir or an unmanaged symlink). Current-layout
   profiles whose `skills/` is a single dir symlink to root are left for
   `/unlink-agentic-grimoire-custom`:
   ```sh
   for profile in .claude-personal .claude-sec; do
     dst="$HOME/$profile/skills"
     [ -L "$dst" ] && continue   # current layout: single dir symlink -> root; /unlink owns it
     [ -d "$dst" ] || continue
     for link in "$dst"/*; do
       [ -L "$link" ] && [ ! -e "$link" ] || continue
       case "$(readlink "$link")" in
         *".agents/skills/"*) rm "$link"; echo "pruned   $link" ;;
       esac
     done
   done
   ```

5. **Report** which memory files were `updated` vs `unchanged`, and confirm the user's
   pre-existing content outside the markers survived (grep a line you saw before the run).
   Note that editing `~/.codex/AGENTS.md` from Claude Code is expected — one run covers both.

**Criterion:** no `$SKILLS` dir or symlink remains in the store or any profile; the managed
block is gone from every memory file with all surrounding user content intact; a second run
reports `unchanged` / no-op everywhere (idempotent); other sources' skills are still installed.
