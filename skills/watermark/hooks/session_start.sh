#!/usr/bin/env bash
# watermark SessionStart hook — records the session's git baseline (high-water mark).
#
# The baseline captures exactly what existed before this session began, so pre-existing
# dirty files are excluded from what `watermark` later commits. Fired by Claude Code and
# Codex SessionStart hooks; both pass a JSON payload on stdin containing `.session_id`.
set -euo pipefail

payload="$(cat 2>/dev/null || true)"

# Extract .session_id from the stdin JSON. Prefer jq; fall back to a portable sed match.
session_id=""
if command -v jq >/dev/null 2>&1; then
  session_id="$(printf '%s' "$payload" | jq -r '.session_id // empty' 2>/dev/null || true)"
fi
if [ -z "$session_id" ]; then
  session_id="$(printf '%s' "$payload" | sed -n 's/.*"session_id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n1)"
fi
[ -n "$session_id" ] || session_id="nosession"

# Only act inside a git work tree; otherwise there is nothing to baseline.
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0

git_dir="$(git rev-parse --git-dir 2>/dev/null)" || exit 0

# Baseline = current dirty state as a dangling commit if the tree is dirty (stash create),
# else HEAD. If HEAD is unborn (no commits yet), use the canonical empty-tree object so the
# whole session shows up as additions.
baseline=""
snap="$(git stash create 2>/dev/null || true)"
if [ -n "$snap" ]; then
  baseline="$snap"
elif head="$(git rev-parse --verify HEAD 2>/dev/null)"; then
  baseline="$head"
else
  baseline="$(git hash-object -t tree /dev/null)"  # empty tree
fi

printf '%s\n' "$baseline" > "$git_dir/watermark-$session_id.baseline"

# `git stash create` does not capture untracked files, so record the pre-existing
# untracked paths separately. watermark subtracts these to avoid claiming a file that
# was already sitting untracked before the session began.
git ls-files --others --exclude-standard > "$git_dir/watermark-$session_id.untracked" 2>/dev/null || true
exit 0
