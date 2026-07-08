---
name: uninstall-agentic-grimoire
description: Fully remove agentic-grimoire — strip the guideline block from ~/.claude/CLAUDE.md and ~/.codex/AGENTS.md (and the custom profiles), then remove this repo's skills from the store and every profile. Never touches skills from other sources. Use when the user says "uninstall agentic-grimoire" or "remove the grimoire skills".
disable-model-invocation: true
---

Goal: cleanly reverse the three onboarding steps (`npx skills add` + `/setup-agentic-grimoire`
+ `/link-agentic-grimoire-custom`) — remove the spliced guideline block and this repo's own
skills — **without touching anything else in the store**.

## Scope boundary (hard rule)

This uninstaller removes **only what this repo published**: the skill directories under this
repo's `skills/` (the `SKILLS` list below) plus the managed `CLAUDE.md` / `AGENTS.md` block.
Skills installed from other sources — Matt Pocock's `ask-matt`, `grilling`, `grill-me`,
`grill-with-docs`, `brand`, `design`, and any other online skill — are **left installed**.
`oracle` and `compass` **are** removed because they are this repo's own `skills/oracle` /
`skills/compass`. Never run `npx skills remove --all`.

## How it works

- `unsplice.sh` (this directory) is the deterministic inverse of `setup-agentic-grimoire`'s
  `splice.sh`: it removes only the region between `<!-- AGENTIC-GRIMOIRE: MANAGED FILE -->` …
  `<!-- END AGENTIC-GRIMOIRE: MANAGED FILE -->` (and the `USER CONTENT` marker line),
  preserving everything the user wrote outside it. No-op on a file without the markers.
- `npx skills remove` removes the store copy and the conventional-profile symlinks. It removes
  **by skill name**, so we pass exactly this repo's published names.
- Removing the store dirs leaves the custom-profile symlinks (`~/.claude-personal`,
  `~/.claude-sec`) dangling; a prune of dead store links finishes the job.

## Steps

Let `DIR` be this skill's own directory (the folder holding this `SKILL.md`, i.e.
`~/.agents/skills/uninstall-agentic-grimoire`).

The published skill set (keep in sync with this repo's `skills/`):

```sh
SKILLS="codewalk compass keystone keystone-react lathe link-agentic-grimoire-custom \
oracle playbook setup-agentic-grimoire storm teach-publish watermark uninstall-agentic-grimoire"
```

1. **Preview the block removal.** Unsplice into throwaway copies and diff, so the user sees
   exactly what leaves each memory file before any real write:
   ```sh
   for f in "$HOME/.claude/CLAUDE.md" "$HOME/.codex/AGENTS.md" \
            "$HOME/.claude-personal/CLAUDE.md" "$HOME/.claude-sec/CLAUDE.md"; do
     [ -e "$f" ] || continue
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
     [ -e "$f" ] && bash "$DIR/unsplice.sh" "$f"
   done
   ```
   Each prints `updated` / `unchanged` (custom profiles no-op unless `/link-agentic-grimoire-custom` ran).

3. **Remove this repo's skills** from the store and the conventional profiles:
   ```sh
   npx skills remove --global -a claude-code codex --yes $SKILLS
   ```
   Only the names in `$SKILLS` are removed. Other sources' skills are untouched.

4. **Prune the now-dangling custom-profile symlinks** (inverse of `link.sh`; removes only dead
   links that point into the store — never a real dir or an unmanaged symlink):
   ```sh
   for profile in .claude-personal .claude-sec; do
     dst="$HOME/$profile/skills"; [ -d "$dst" ] || continue
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
