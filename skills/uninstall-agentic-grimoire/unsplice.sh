#!/usr/bin/env bash
# unsplice.sh <target-file>
#
# Inverse of splice.sh: remove the AGENTIC-GRIMOIRE managed block from <target-file>,
# preserving every other line the user wrote. Deterministic: no LLM, pure text.
#
#   - target absent / empty / no markers -> no-op (unchanged)
#   - target has BEGIN..END               -> delete that region AND the USER CONTENT marker
#                                            line, keep all other content verbatim
#   - already clean                        -> no write (idempotent, no churn)
#
# Never deletes the file, even if the managed block was its only content.
set -euo pipefail

target="${1:?usage: unsplice.sh <target-file>}"

BEGIN="<!-- AGENTIC-GRIMOIRE: MANAGED FILE -->"
END="<!-- END AGENTIC-GRIMOIRE: MANAGED FILE -->"
USER_MARK="<!-- AGENTIC-GRIMOIRE: USER CONTENT -->"

if [ ! -s "$target" ]; then
  echo "unchanged $target"
  exit 0
fi

if ! grep -qF "$BEGIN" "$target" || ! grep -qF "$END" "$target"; then
  echo "unchanged $target"
  exit 0
fi

old="$(cat "$target")"

# Drop the BEGIN..END region (inclusive) and the USER CONTENT marker line; keep the rest.
new="$(awk -v b="$BEGIN" -v e="$END" -v um="$USER_MARK" '
  index($0, b) { skip = 1; next }
  skip && index($0, e) { skip = 0; next }
  skip { next }
  index($0, um) { next }
  { print }
' "$target")"

# Trim leading blank lines left behind when the block sat at the top of the file.
new="$(printf '%s\n' "$new" | awk 'NF { started = 1 } started { print }')"

if [ "$new" = "$old" ]; then
  echo "unchanged $target"
else
  printf '%s\n' "$new" > "$target"
  echo "updated $target"
fi
