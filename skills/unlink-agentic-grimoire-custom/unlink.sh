#!/usr/bin/env bash
# unlink.sh [--target DIR] [--dry-run] [profile ...]
#
# Inverse of link.sh: remove the config symlinks that link.sh created in each custom Claude
# profile (default .claude-personal and .claude-sec) and restore the original from
# <profile>/backups/<item>-<ts> if one is there, so the profile owns its config again instead
# of mirroring root.
#
# Hard boundary: account-bound files (.claude.json + Keychain auth), settings, and all
# runtime/knowledge state are NEVER touched — the tool only acts on the fixed config allowlist,
# and a denylist assertion is defence-in-depth.
#
# Safety: only removes a symlink whose value EQUALS what link.sh would have created (i.e. points
# into root) — never a real file/dir or a foreign symlink; restores the most-recent backup via
# mv (which consumes it); re-running is idempotent (real/absent items are skipped).
set -euo pipefail

# ---- config --------------------------------------------------------------------------
target="$HOME/.claude"
dry=false
profiles=()

CONFIG_ITEMS=(CLAUDE.md RTK.md rules skills agents commands)

# Never touch these, even if a future edit adds them to CONFIG_ITEMS.
DENY=(.claude.json .credentials.json settings.json settings.local.json
      sessions session-env shell-snapshots paste-cache cache tmp jobs tasks
      telemetry stats-cache.json daemon debug plugins backups ide chrome
      policy-limits.json remote-settings.json mcp-needs-auth-cache.json
      projects plans history.jsonl)

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

# The symlink value link.sh would have written for <item> at <profile_dir> — relative when both
# dirs share a parent (the normal case: everything under $HOME), else absolute. Identical logic
# to link.sh so "ours" is defined exactly as link created it.
link_value() {
  local profile_dir="$1" item="$2"
  if [ "$(dirname "$profile_dir")" = "$(dirname "$target")" ]; then
    printf '../%s/%s' "$(basename "$target")" "$item"
  else
    printf '%s/%s' "$target" "$item"
  fi
}

# Remove <profile_dir>/<item> only if it is a symlink we created, then restore any backup.
unlink_item() {
  local profile_dir="$1" item="$2"
  if is_denied "$item"; then echo "  REFUSE $item (denylisted)"; return; fi

  local link="$profile_dir/$item"
  local want; want="$(link_value "$profile_dir" "$item")"

  if [ ! -L "$link" ]; then
    if [ -e "$link" ]; then echo "  skip   $item (real file/dir, not a link)"
    else echo "  skip   $item (absent)"; fi
    return
  fi
  if [ "$(readlink "$link")" != "$want" ]; then
    echo "  skip   $item (foreign link -> $(readlink "$link"))"; return
  fi

  run rm "$link"
  local bk; bk="$(ls -1dt "$profile_dir/backups/$item-"* 2>/dev/null | head -1 || true)"
  if [ -n "$bk" ]; then
    run mv "$bk" "$link"
    echo "  restore $item <- backups/$(basename "$bk")"
  else
    echo "  unlink  $item (removed; no backup to restore)"
  fi
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

  for item in "${CONFIG_ITEMS[@]}"; do unlink_item "$profile_dir" "$item"; done
done

echo
$dry && echo "dry-run only — nothing changed." || echo "done."
