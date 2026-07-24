---
name: sync-agentic-grimoire
description: Sync this machine's agentic-grimoire skills with the repo — update changed skills, prune deleted skills, and repair stale profile shadows.
disable-model-invocation: true
---

## Why this exists

`npx skills update --global` re-syncs *changed* skills but, at global scope, **does not prune**
skills deleted from the source repo — they linger as stale installs (upstream issue
[#415](https://github.com/vercel-labs/skills/issues/415)). Older installs can also leave real
skill directories under agent-specific roots, shadowing the current canonical copy. This skill
updates changed skills, prunes deleted ones, and reconciles those profile shadows.

## Scope boundary (hard rule)

Prune or reconcile **only** skills whose `~/.agents/.skill-lock.json` source is exactly
`healthier-vitamins/agentic-grimoire`. The initial `npx skills update --global` may update
changed skills from any globally tracked source; this workflow never removes or relinks those
other sources. Their profile entries are reported as untouched. Never run
`npx skills remove --all`.

## How it works

- `npx skills update --global` handles the *changed* half (GitHub Tree SHA diff → re-`add`).
- `sync.sh` (this directory) computes the *prune set*, read-only: the skills installed from
  this repo (per `~/.agents/.skill-lock.json`) minus the repo's current `skills/` dirs (fetched live
  from the GitHub Contents API). It prints one name per line and **removes nothing** — the
  removal decision stays here, behind a confirm gate.
- `reconcile.sh` audits normal profile roots, read-only by default:
  - Claude Code entries owned by this repo must link to `~/.agents/skills/<name>`.
  - Codex reads `~/.agents/skills` directly, so owned legacy entries under
    `~/.codex/skills` must be removed rather than relinked.
  - Unowned entries are printed as `UNTOUCHED` and never changed.
- If the GitHub fetch fails or is rate-limited, `sync.sh` exits non-zero and prunes nothing;
  do not guess a list — tell the user to retry.

## Steps

Let `DIR` be this skill's own directory (the folder holding this `SKILL.md`, i.e.
`~/.agents/skills/sync-agentic-grimoire`).

1. **Update changed skills:**
   ```bash
   npx skills update --global
   ```

2. **Create a persistent combined preview:**
   ```bash
   set -euo pipefail
   DIR="$HOME/.agents/skills/sync-agentic-grimoire"
   SYNC_RUN_DIR="$(mktemp -d "${TMPDIR:-/tmp}/agentic-grimoire-sync.XXXXXX")"
   PRUNE_FILE="$SYNC_RUN_DIR/prune"
   RECONCILE_PREVIEW="$SYNC_RUN_DIR/reconcile-preview"
   RECONCILE_HELPER="$SYNC_RUN_DIR/reconcile.sh"

   cleanup_preview() {
     rm -f -- "$PRUNE_FILE" "$RECONCILE_PREVIEW" "$RECONCILE_HELPER"
     rmdir -- "$SYNC_RUN_DIR"
   }

   if ! cp "$DIR/reconcile.sh" "$RECONCILE_HELPER"; then
     cleanup_preview
     exit 2
   fi

   if ! bash "$DIR/sync.sh" > "$PRUNE_FILE"; then
     cleanup_preview
     exit 2
   fi
   if ! bash "$RECONCILE_HELPER" --exclude-file "$PRUNE_FILE" > "$RECONCILE_PREVIEW"; then
     cleanup_preview
     exit 2
   fi

   echo "preview directory: $SYNC_RUN_DIR"
   if [ -s "$PRUNE_FILE" ]; then
     while IFS= read -r name; do
       echo "REMOVE    deleted     $name (installed from agentic-grimoire, gone from repo)"
     done < "$PRUNE_FILE"
   fi
   while IFS= read -r line; do
     IFS=$'\t' read -r verb scope name state <<< "$line"
     if [ "$verb" = PRUNE ]; then
       echo "REMOVE    deleted-path $scope/$name [state: $state]"
     else
       echo "$line"
     fi
   done < "$RECONCILE_PREVIEW"
   ```
   - A non-zero exit from either script means **stop**; the failed preview is cleaned up and
     nothing is pruned or reconciled.
   - Record the exact printed preview directory. It deliberately survives the tool call and
     confirmation turn.
   - `reconcile.sh` prints `LINK`/`RELINK` for Claude Code, `REMOVE` for legacy Codex
     entries, and `UNTOUCHED` for entries outside this repo's ownership. Action lines include
     a state fingerprint so apply can detect a replaced directory or changed symlink.

3. **Combined confirm gate.** Show the complete preview and ask for one explicit confirmation
   **before** changing or removing anything. If the user declines, remove only the three files
   inside the printed preview directory, then `rmdir` that exact directory.

4. **Revalidate and apply (only after the user confirms):**
   ```bash
   set -euo pipefail
   DIR="$HOME/.agents/skills/sync-agentic-grimoire"
   SYNC_RUN_DIR="<exact preview directory printed in step 2>"
   PRUNE_FILE="$SYNC_RUN_DIR/prune"
   RECONCILE_PREVIEW="$SYNC_RUN_DIR/reconcile-preview"
   RECONCILE_HELPER="$SYNC_RUN_DIR/reconcile.sh"
   LOCK="$HOME/.agents/.skill-lock.json"
   SOURCE="healthier-vitamins/agentic-grimoire"
   CURRENT_PRUNE="$SYNC_RUN_DIR/current-prune"
   CURRENT_RECONCILE="$SYNC_RUN_DIR/current-reconcile"

   [ -f "$PRUNE_FILE" ] && [ -f "$RECONCILE_PREVIEW" ] && [ -f "$RECONCILE_HELPER" ] || {
     echo "error: incomplete sync preview: $SYNC_RUN_DIR" >&2
     exit 2
   }

   bash "$DIR/sync.sh" > "$CURRENT_PRUNE"
   bash "$RECONCILE_HELPER" --exclude-file "$CURRENT_PRUNE" > "$CURRENT_RECONCILE"

   if ! cmp -s "$PRUNE_FILE" "$CURRENT_PRUNE"; then
     diff -u "$PRUNE_FILE" "$CURRENT_PRUNE" || true
     echo "error: deleted-skill set changed; preview and confirm again" >&2
     rm -f -- "$CURRENT_PRUNE" "$CURRENT_RECONCILE"
     exit 2
   fi
   if ! cmp -s "$RECONCILE_PREVIEW" "$CURRENT_RECONCILE"; then
     diff -u "$RECONCILE_PREVIEW" "$CURRENT_RECONCILE" || true
     echo "error: profile state changed; preview and confirm again" >&2
     rm -f -- "$CURRENT_PRUNE" "$CURRENT_RECONCILE"
     exit 2
   fi

   if [ -s "$CURRENT_PRUNE" ]; then
     PRUNE_NAMES=()
     while IFS= read -r name; do PRUNE_NAMES+=("$name"); done < "$CURRENT_PRUNE"
     npx skills remove --global -a claude-code codex --yes "${PRUNE_NAMES[@]}"

     if [ -f "$LOCK" ]; then
       jq -e '(.skills // {}) | type == "object"' "$LOCK" >/dev/null
       removal_failed=false
       for name in "${PRUNE_NAMES[@]}"; do
         if jq -e --arg name "$name" --arg src "$SOURCE" \
           '(.skills // {})[$name].source? == $src' "$LOCK" >/dev/null; then
           echo "error: skills CLI left $name in the $SOURCE lock registry" >&2
           removal_failed=true
         fi
       done
       $removal_failed && exit 2
     fi
   fi

   bash "$RECONCILE_HELPER" --apply --expect "$CURRENT_RECONCILE" \
     --exclude-file "$CURRENT_PRUNE"
   rm -f -- "$PRUNE_FILE" "$RECONCILE_PREVIEW" "$CURRENT_PRUNE" \
     "$CURRENT_RECONCILE" "$RECONCILE_HELPER"
   rmdir -- "$SYNC_RUN_DIR"
   ```
   `sync.sh` validates every prune name as a non-hidden lowercase skill slug before it reaches
   `npx` or a filesystem path. Any command failure stops the phase. After registry removal,
   `reconcile.sh` accepts an absent path or the exact confirmed fingerprint and refuses any other
   state. It also refuses symlinked profile roots and non-symlink aliases of the canonical store.

5. **Reminders** (no automatic invocation):
   - Inspect `~/.claude-personal/skills` and `~/.claude-sec/skills`. If an existing custom
     profile does not resolve to root `~/.claude/skills`, tell the user to run
     `/link-agentic-grimoire-custom`. Do not mutate custom profiles here. Once linked, they
     inherit root's updated and pruned skill set live.
   - Tell the user to re-run `/setup-agentic-grimoire` if the guideline block changed upstream.

**Criterion:** every skill still installed from this source exists in the repo; Claude Code
entries resolve to the canonical store; no grimoire-owned legacy Codex entries remain; other
sources' entries are reported and untouched; a second apply run makes no changes (idempotent).
