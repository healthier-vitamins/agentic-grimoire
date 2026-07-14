---
name: setup-agentic-grimoire
description: Splice the agentic-grimoire guideline block into ~/.claude/CLAUDE.md and ~/.codex/AGENTS.md, append-only and idempotent. Run once after installing the skills.
disable-model-invocation: true
---

Skills are linked into profiles by `npx skills add healthier-vitamins/agentic-grimoire`.
This skill covers the one thing that CLI never touches: the `CLAUDE.md` / `AGENTS.md` files.

## How it works

`splice.sh` (this directory) does a deterministic, idempotent text splice between the markers
`<!-- AGENTIC-GRIMOIRE: MANAGED FILE -->` … `<!-- END AGENTIC-GRIMOIRE: MANAGED FILE -->`:
a re-run replaces only that block; anything the user wrote outside it is preserved (existing
unmarked content is demoted below a `<!-- AGENTIC-GRIMOIRE: USER CONTENT -->` marker, never lost).

## Steps

Let `DIR` be this skill's own directory (the folder holding this `SKILL.md`, i.e.
`~/.agents/skills/setup-agentic-grimoire`).

1. **Preview.** Splice into a throwaway copy and diff it, so the user sees the change before any real write:
   ```sh
   for pair in "$HOME/.claude/CLAUDE.md:claude" "$HOME/.codex/AGENTS.md:codex"; do
     f="${pair%:*}"; b="${pair##*:}"; tmp="$(mktemp)"
     [ -e "$f" ] && cp "$f" "$tmp"
     bash "$DIR/splice.sh" "$tmp" "$DIR/blocks/$b.md" >/dev/null
     echo "=== $f ==="; diff -u "$f" "$tmp" 2>/dev/null || true; rm -f "$tmp"
   done
   ```

2. **Apply** both profiles:
   ```sh
   bash "$DIR/splice.sh" ~/.claude/CLAUDE.md  "$DIR/blocks/claude.md"
   bash "$DIR/splice.sh" ~/.codex/AGENTS.md   "$DIR/blocks/codex.md"
   ```
   Each command prints `created` / `updated` / `unchanged`.

3. **Report** which files were `updated` vs `unchanged`, and confirm the user's pre-existing
   content is still present (grep for a line you saw before the run). Note that editing
   `~/.codex/AGENTS.md` from Claude Code is expected — one run covers both agents.

**Criterion:** both files contain exactly one managed block between the markers; all
pre-existing user content survives; a second run reports `unchanged` for both (idempotent).

## Next

To also cover the custom profiles `~/.claude-personal` and `~/.claude-sec`, run
`/link-agentic-grimoire-custom`.
