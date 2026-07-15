#!/usr/bin/env bash
# link.sh [--target DIR] [--dry-run] [profile ...]
#
# Mirror root ~/.claude's config into the custom Claude profiles (default .claude-personal
# and .claude-sec) via relative symlinks, so their config never drifts from root. Root's
# skills/ is itself a symlink farm over the ~/.agents/skills store, so linking skills/ to root
# transitively tracks the store plus any root-local skills.
#
# Hard boundary: account-bound files (.claude.json + Keychain auth), settings, and all
# runtime/knowledge state are NEVER touched — the tool only acts on a fixed config allowlist,
# and a denylist assertion is defence-in-depth.
#
# Safety: relative symlinks; a real file/dir is backed up (never deleted) before it is
# replaced; re-running is idempotent (already-linked items are skipped).
set -euo pipefail

# ---- config --------------------------------------------------------------------------
target="$HOME/.claude"
dry=false
profiles=()

CONFIG_ITEMS=(CLAUDE.md RTK.md rules skills agents commands)

# Never symlink these, even if a future edit adds them to CONFIG_ITEMS.
DENY=(.claude.json .credentials.json settings.json settings.local.json
      sessions session-env shell-snapshots paste-cache cache tmp jobs tasks
      telemetry stats-cache.json daemon debug plugins backups ide chrome
      policy-limits.json remote-settings.json mcp-needs-auth-cache.json
      projects plans history.jsonl)

ts="$(date +%Y%m%d-%H%M%S)"

# ---- args ----------------------------------------------------------------------------
while [ "$#" -gt 0 ]; do
  case "$1" in
    --target) target="$2"; shift 2 ;;
    --dry-run) dry=true; shift ;;
    -h|--help) grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    -*) echo "error: unknown option $1" >&2; exit 2 ;;
    *) profiles+=("$1"); shift ;;
  esac
done
[ "${#profiles[@]}" -gt 0 ] || profiles=(.claude-personal .claude-sec)

[ -d "$target" ] || { echo "error: target $target is not a directory" >&2; exit 1; }
target="$(cd "$target" && pwd)"   # normalise to absolute

is_denied() { local x; for x in "${DENY[@]}"; do [ "$1" = "$x" ] && return 0; done; return 1; }

run() { if $dry; then echo "  DRY  $*"; else "$@"; fi; }

# Compute the symlink value for <item> at <profile_dir>, relative when both dirs share a
# parent (the normal case: everything under $HOME), else absolute.
link_value() {
  local profile_dir="$1" item="$2"
  if [ "$(dirname "$profile_dir")" = "$(dirname "$target")" ]; then
    printf '../%s/%s' "$(basename "$target")" "$item"
  else
    printf '%s/%s' "$target" "$item"
  fi
}

# Symlink <profile_dir>/<item> -> target/<item>, backing up anything real first.
link_item() {
  local profile_dir="$1" item="$2"
  if is_denied "$item"; then echo "  REFUSE $item (denylisted)"; return; fi

  local link="$profile_dir/$item"
  local want; want="$(link_value "$profile_dir" "$item")"

  if [ ! -e "$target/$item" ]; then echo "  skip   $item (absent in root)"; return; fi

  if [ -L "$link" ]; then
    if [ "$(readlink "$link")" = "$want" ]; then echo "  ok     $item (already linked)"; return; fi
    run rm "$link"                                   # unmanaged/other symlink -> replace
  elif [ -e "$link" ]; then
    run mkdir -p "$profile_dir/backups"
    run mv "$link" "$profile_dir/backups/$item-$ts"  # real file/dir -> preserve
    echo "  backup $item -> backups/$item-$ts"
  fi
  run ln -s "$want" "$link"
  echo "  link   $item -> $want"
}

# ---- run -----------------------------------------------------------------------------
echo "target (source of truth): $target"
$dry && echo "mode: dry-run"

for profile in "${profiles[@]}"; do
  profile_dir="$HOME/$profile"
  echo
  echo "== $profile =="
  if [ ! -d "$profile_dir" ]; then echo "  skip (no such profile dir)"; continue; fi
  if [ "$profile_dir" -ef "$target" ]; then echo "  skip (this IS the target)"; continue; fi

  for item in "${CONFIG_ITEMS[@]}"; do link_item "$profile_dir" "$item"; done
done

echo
$dry && echo "dry-run only — nothing changed." || echo "done."
