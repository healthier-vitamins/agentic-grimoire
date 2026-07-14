---
name: link-agentic-grimoire-custom
description: Extend agentic-grimoire setup to the custom Claude profiles ~/.claude-personal and ~/.claude-sec — symlink the skill store and splice the guideline block. Run after /setup-agentic-grimoire.
disable-model-invocation: true
---

Prerequisite: `npx skills add healthier-vitamins/agentic-grimoire --global` has run (the store
`~/.agents/skills` exists) and ideally `/setup-agentic-grimoire` too (it installs the shared
block + splice helper this skill reuses).

Let `DIR` be this skill's own directory; let `SETUP=~/.agents/skills/setup-agentic-grimoire`
(the sibling skill that holds `blocks/claude.md` and `splice.sh`).

## Steps

1. **Symlink the store** into both custom profiles (safe: preserves any real dir you placed
   there, prunes only dead store links):
   ```sh
   bash "$DIR/link.sh"          # defaults to .claude-personal and .claude-sec
   ```

2. **Splice the guideline block** into each custom profile's `CLAUDE.md` (append-only, idempotent):
   ```sh
   bash "$SETUP/splice.sh" ~/.claude-personal/CLAUDE.md "$SETUP/blocks/claude.md"
   bash "$SETUP/splice.sh" ~/.claude-sec/CLAUDE.md      "$SETUP/blocks/claude.md"
   ```
   If `$SETUP` is missing, run `/setup-agentic-grimoire` first (or point `SETUP` at this repo's
   `skills/setup-agentic-grimoire`).

3. **Report** per profile: how many skills were `linked` / `skipped (real dir preserved)` /
   `pruned`, and whether each `CLAUDE.md` was `updated` or `unchanged`. Confirm any pre-existing
   real skill dirs and user content are intact.

**Criterion:** each custom profile's `skills/` mirrors the store via relative symlinks with no
real dir destroyed; each `CLAUDE.md` has one managed block with user content preserved; a second
run is idempotent (`unchanged` / already-linked).
