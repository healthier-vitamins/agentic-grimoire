#!/usr/bin/env bash
# sync.sh
#
# Print the prune set: skills installed from THIS repo (per ~/.agents/.skill-lock.json)
# that no longer exist in the repo's skills/ dir on GitHub. One name per line, stdout.
# Read-only — never removes anything; the caller previews, confirms, then runs
# `npx skills remove`. Diagnostics go to stderr.
#
#   - no lockfile / nothing installed from this source -> no output, exit 0
#   - GitHub fetch fails / rate-limited (object, not array) -> abort, exit 2, prune nothing
set -euo pipefail

SOURCE="healthier-vitamins/agentic-grimoire"
LOCK="$HOME/.agents/.skill-lock.json"
API="https://api.github.com/repos/$SOURCE/contents/skills"

if [ ! -f "$LOCK" ]; then
  echo "no lockfile at $LOCK — nothing installed from $SOURCE." >&2
  exit 0
fi

installed="$(jq -r --arg src "$SOURCE" \
  '.skills // {} | to_entries[] | select(.value.source == $src) | .key' "$LOCK")"

if [ -z "$installed" ]; then
  echo "no skills installed from $SOURCE — nothing to prune." >&2
  exit 0
fi

resp="$(curl -fsSL "$API" 2>/dev/null)" || {
  echo "error: could not reach GitHub ($API). Offline or rate-limited (60/hr unauth)." >&2
  echo "No skills pruned — retry later." >&2
  exit 2
}

# Rate-limit / error responses are a JSON object, not the expected directory array.
if ! printf '%s' "$resp" | jq -e 'type == "array"' >/dev/null 2>&1; then
  msg="$(printf '%s' "$resp" | jq -r '.message // "unexpected response"' 2>/dev/null)"
  echo "error: GitHub API did not return a listing ($msg). Rate-limited or offline." >&2
  echo "No skills pruned — retry later." >&2
  exit 2
fi

repo="$(printf '%s' "$resp" | jq -r '.[] | select(.type == "dir") | .name')"

# Prune set = installed-from-source MINUS repo-current.
comm -23 <(printf '%s\n' "$installed" | sort) <(printf '%s\n' "$repo" | sort)
