#!/usr/bin/env bash
# sync.sh
#
# Print the prune set: skills installed from THIS repo (per ~/.agents/.skill-lock.json)
# that no longer exist in the repo's skills/ dir on GitHub. One name per line, stdout.
# Read-only — never removes anything; the caller previews, confirms, then runs
# `npx skills remove`. Diagnostics go to stderr.
#
# The listing is fetched through `gh api` when the GitHub CLI is installed and logged in
# (5000 req/hr), falling back to unauthenticated curl (60 req/hr) otherwise.
#
#   - no lockfile / nothing installed from this source -> no output, exit 0
#   - both fetches fail, or the response is an object rather than the expected directory
#     array (offline, rate-limited, repo renamed) -> abort, exit 2, prune nothing
set -euo pipefail

SOURCE="healthier-vitamins/agentic-grimoire"
LOCK="$HOME/.agents/.skill-lock.json"
API="https://api.github.com/repos/$SOURCE/contents/skills"

if [ ! -f "$LOCK" ]; then
  echo "no lockfile at $LOCK — nothing installed from $SOURCE." >&2
  exit 0
fi
if ! jq -e '(.skills // {}) | type == "object"' "$LOCK" >/dev/null; then
  echo "error: invalid skill lockfile: $LOCK" >&2
  exit 2
fi

validate_names() {
  local label="$1" names="$2" name
  while IFS= read -r name; do
    case "$name" in
      ""|.*|-*|*[!a-z0-9-]*)
        echo "error: unsafe $label skill name: $name" >&2
        exit 2
        ;;
    esac
  done <<< "$names"
}

installed="$(jq -r --arg src "$SOURCE" \
  '.skills // {} | to_entries[] | select(.value.source == $src) | .key' "$LOCK")"

if [ -z "$installed" ]; then
  echo "no skills installed from $SOURCE — nothing to prune." >&2
  exit 0
fi

validate_names "installed" "$installed"

# Prefer the authenticated CLI: the anonymous API allows only 60 requests/hr, and
# exhausting it is the common reason this script aborts. Capture gh's output before
# emitting any of it, so a partial body can never be concatenated with curl's response.
fetch_listing() {
  local out
  if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
    if out="$(gh api "repos/$SOURCE/contents/skills" 2>/dev/null)"; then
      printf '%s' "$out"
      return 0
    fi
  fi
  curl -fsSL "$API" 2>/dev/null
}

resp="$(fetch_listing)" || {
  echo "error: could not reach GitHub ($API) via gh or curl. Offline, or rate-limited" >&2
  echo "(60/hr unauthenticated — run 'gh auth login' to raise it to 5000/hr)." >&2
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
validate_names "repository" "$repo"

# Prune set = installed-from-source MINUS repo-current.
comm -23 <(printf '%s\n' "$installed" | sort) <(printf '%s\n' "$repo" | sort)
