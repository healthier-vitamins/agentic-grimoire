#!/usr/bin/env bash
# splice.sh <target-file> <block-file>
#
# Idempotently splice <block-file> into <target-file> between the AGENTIC-GRIMOIRE
# markers, preserving every line the user wrote. Deterministic: no LLM, pure text.
#
#   - target absent/empty         -> write just the managed block
#   - target has BEGIN..END        -> replace only that region, keep the rest verbatim
#   - target has content, no marks -> managed block on top, user content below a marker
#   - already identical            -> no write (idempotent, no churn)
set -euo pipefail

target="${1:?usage: splice.sh <target-file> <block-file>}"
block_file="${2:?usage: splice.sh <target-file> <block-file>}"

BEGIN="<!-- AGENTIC-GRIMOIRE: MANAGED FILE -->"
END="<!-- END AGENTIC-GRIMOIRE: MANAGED FILE -->"
USER_MARK="<!-- AGENTIC-GRIMOIRE: USER CONTENT -->"

managed="$(printf '%s\n' "$BEGIN"; cat "$block_file"; printf '%s\n' "$END")"

mkdir -p "$(dirname "$target")"

if [ ! -s "$target" ]; then
  printf '%s\n' "$managed" > "$target"
  echo "created $target"
  exit 0
fi

old="$(cat "$target")"

if grep -qF "$BEGIN" "$target" && grep -qF "$END" "$target"; then
  # Replace the existing managed region in place; keep text before and after it.
  new="$(awk -v bf="$block_file" -v b="$BEGIN" -v e="$END" '
    BEGIN {
      mgd = b "\n"
      while ((getline line < bf) > 0) mgd = mgd line "\n"
      mgd = mgd e
    }
    index($0, b) { if (!done) { print mgd; done = 1 } skip = 1; next }
    skip && index($0, e) { skip = 0; next }
    !skip { print }
  ' "$target")"
else
  # No markers yet: prepend the managed block, preserve user content below a marker.
  new="$(printf '%s\n\n%s\n\n%s' "$managed" "$USER_MARK" "$old")"
fi

if [ "$new" = "$old" ]; then
  echo "unchanged $target"
else
  printf '%s\n' "$new" > "$target"
  echo "updated $target"
fi
