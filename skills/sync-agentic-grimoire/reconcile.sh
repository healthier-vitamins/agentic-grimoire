#!/usr/bin/env bash
# reconcile.sh [--apply --expect FILE] [--exclude-file FILE]
#
# Audit or repair the normal Claude Code and Codex skill roots for skills owned by
# healthier-vitamins/agentic-grimoire.
#
# Default mode is read-only. With --apply:
#   - Claude Code entries are linked to the canonical ~/.agents/skills store.
#   - Legacy Codex entries are removed; current Codex reads the canonical store directly.
#
# Entries not proven to be owned by this repo are reported and never changed.
set -euo pipefail
if [ -z "${HOME:-}" ] || [ "$HOME" = "/" ]; then
  echo "error: refusing to reconcile with an empty or root HOME" >&2
  exit 2
fi

SOURCE="healthier-vitamins/agentic-grimoire"
LOCK="$HOME/.agents/.skill-lock.json"
STORE="$HOME/.agents/skills"
CLAUDE_SKILLS="$HOME/.claude/skills"
CODEX_SKILLS="$HOME/.codex/skills"

apply=false
exclude_file=""
expected_file=""

while [ "$#" -gt 0 ]; do
  case "$1" in
    --apply) apply=true; shift ;;
    --exclude-file)
      [ "$#" -ge 2 ] || { echo "error: --exclude-file requires a path" >&2; exit 2; }
      exclude_file="$2"; shift 2
      ;;
    --expect)
      [ "$#" -ge 2 ] || { echo "error: --expect requires a path" >&2; exit 2; }
      expected_file="$2"; shift 2
      ;;
    -h|--help) sed -n 's/^# \{0,1\}//p' "$0"; exit 0 ;;
    *) echo "error: unknown argument $1" >&2; exit 2 ;;
  esac
done

if $apply && [ -z "$expected_file" ]; then
  echo "error: --apply requires --expect FILE from the confirmed preview" >&2
  exit 2
fi
if [ -n "$expected_file" ] && [ ! -f "$expected_file" ]; then
  echo "error: expected preview does not exist: $expected_file" >&2
  exit 2
fi

if [ ! -f "$LOCK" ]; then
  echo "no lockfile at $LOCK — no $SOURCE profile entries can be proven safe to reconcile." >&2
  exit 0
fi

if [ -n "$exclude_file" ] && [ ! -f "$exclude_file" ]; then
  echo "error: exclude file does not exist: $exclude_file" >&2
  exit 2
fi

if ! jq -e '(.skills // {}) | type == "object"' "$LOCK" >/dev/null; then
  echo "error: invalid skill lockfile: $LOCK" >&2
  exit 2
fi

validate_roots() {
  local root
  if [ -L "$STORE" ]; then
    echo "error: canonical store must not be a symlink: $STORE" >&2
    return 1
  fi
  if [ ! -d "$STORE" ] && { ! $apply || [ "${#owned[@]}" -gt 0 ]; }; then
    echo "error: canonical store is missing: $STORE" >&2
    return 1
  fi
  for root in "$CLAUDE_SKILLS" "$CODEX_SKILLS"; do
    if [ -L "$root" ]; then
      echo "error: refusing to reconcile a symlinked profile root: $root" >&2
      return 1
    fi
    if [ -e "$root" ] && [ ! -d "$root" ]; then
      echo "error: profile root is not a directory: $root" >&2
      return 1
    fi
    if [ -d "$root" ] && [ "$root" -ef "$STORE" ]; then
      echo "error: profile root resolves to the canonical store: $root" >&2
      return 1
    fi
  done
}
owned=()
while IFS= read -r name; do
  case "$name" in
    ""|.*|-*|*[!a-z0-9-]*)
      echo "error: unsafe skill name in $LOCK: $name" >&2
      exit 2
      ;;
    *) owned+=("$name") ;;
  esac
done < <(jq -r --arg src "$SOURCE" \
  '.skills // {} | to_entries[] | select(.value.source == $src) | .key' "$LOCK")

excluded=()
if [ -n "$exclude_file" ]; then
  while IFS= read -r name; do
    case "$name" in
      ""|.*|-*|*[!a-z0-9-]*)
        echo "error: unsafe excluded skill name: $name" >&2
        exit 2
        ;;
      *) excluded+=("$name") ;;
    esac
  done < "$exclude_file"
fi

is_owned() {
  local candidate="$1" name
  for name in "${owned[@]+"${owned[@]}"}"; do
    [ "$candidate" = "$name" ] && return 0
  done
  return 1
}

is_excluded() {
  local candidate="$1" excluded_name
  for excluded_name in "${excluded[@]+"${excluded[@]}"}"; do
    [ "$candidate" = "$excluded_name" ] && return 0
  done
  return 1
}

expect_action() {
  local wanted="$1" line
  while IFS= read -r line; do
    [ "$line" = "$wanted" ] && return 0
  done < "$expected_file"
  echo "error: action state changed or was not confirmed: $wanted" >&2
  return 1
}

entry_signature() {
  local entry="$1" target checksum
  if [ -L "$entry" ]; then
    target="$(readlink "$entry")"
    printf "symlink:%q" "$target"
  elif [ -d "$entry" ]; then
    checksum="$(cd "$entry" && tar -cf - . | cksum)"
    printf "directory:%s" "$checksum"
  elif [ -f "$entry" ]; then
    checksum="$(cksum < "$entry")"
    printf "file:%s" "$checksum"
  elif [ -e "$entry" ]; then
    printf "other"
  else
    printf "absent"
  fi
}

remove_entry() {
  local entry="$1"
  rm -rf -- "$entry"
}

reconcile_claude() {
  local name="$1" canonical="$STORE/$1" entry="$CLAUDE_SKILLS/$1"
  local want="../../.agents/skills/$1" signature action_line

  if [ -L "$entry" ] && [ "$entry" -ef "$canonical" ]; then
    echo "OK        claude-code $name -> canonical store"
    return
  fi

  signature="$(entry_signature "$entry")"
  if [ "$signature" = absent ]; then
    action_line="LINK      claude-code $name -> canonical store [state: absent]"
    if $apply; then
      expect_action "$action_line"
      mkdir -p "$CLAUDE_SKILLS"
      ln -s "$want" "$entry"
      echo "LINKED    claude-code $name -> canonical store"
    else
      echo "$action_line"
    fi
    return
  fi

  action_line="RELINK    claude-code $name -> canonical store [state: $signature]"
  if $apply; then
    expect_action "$action_line"
    remove_entry "$entry"
    ln -s "$want" "$entry"
    echo "RELINKED  claude-code $name -> canonical store"
  else
    echo "$action_line"
  fi
}

reconcile_codex() {
  local name="$1" entry="$CODEX_SKILLS/$1" signature action_line

  signature="$(entry_signature "$entry")"
  if [ "$signature" = absent ]; then
    echo "OK        codex       $name (canonical store only)"
    return
  fi

  action_line="REMOVE    codex       $name legacy entry [state: $signature]"
  if $apply; then
    expect_action "$action_line"
    remove_entry "$entry"
    echo "REMOVED   codex       $name legacy entry"
  else
    echo "$action_line"
  fi
}

prune_path() {
  local scope="$1" name="$2"
  case "$scope" in
    store) printf "%s/%s" "$STORE" "$name" ;;
    claude-code) printf "%s/%s" "$CLAUDE_SKILLS" "$name" ;;
    codex) printf "%s/%s" "$CODEX_SKILLS" "$name" ;;
    *) echo "error: unknown prune scope: $scope" >&2; return 2 ;;
  esac
}

prune_manifest_line() {
  local scope="$1" name="$2" signature="$3"
  printf "PRUNE\t%s\t%s\t%s" "$scope" "$name" "$signature"
}

expect_prune_state() {
  local scope="$1" name="$2" current="$3"
  local verb expected_scope expected_name expected rest found=false
  while IFS=$'\t' read -r verb expected_scope expected_name expected rest; do
    if [ "$verb" = PRUNE ] && [ "$expected_scope" = "$scope" ] && [ "$expected_name" = "$name" ]; then
      found=true
      if [ "$current" = absent ] || [ "$current" = "$expected" ]; then return 0; fi
      break
    fi
  done < "$expected_file"
  if ! $found; then
    echo "error: prune path was not confirmed: $scope/$name" >&2
  else
    echo "error: prune path changed after confirmation: $scope/$name" >&2
  fi
  return 1
}

preview_pruned_paths() {
  local name scope entry signature
  for name in "${excluded[@]+"${excluded[@]}"}"; do
    is_owned "$name" || { echo "error: excluded skill is not owned by $SOURCE: $name" >&2; return 2; }
    for scope in store claude-code codex; do
      entry="$(prune_path "$scope" "$name")"
      signature="$(entry_signature "$entry")"
      prune_manifest_line "$scope" "$name" "$signature"
      echo
    done
  done
}

apply_pruned_paths() {
  local name scope entry signature
  for name in "${excluded[@]+"${excluded[@]}"}"; do
    for scope in claude-code codex store; do
      entry="$(prune_path "$scope" "$name")"
      signature="$(entry_signature "$entry")"
      expect_prune_state "$scope" "$name" "$signature"
    done
  done
  for name in "${excluded[@]+"${excluded[@]}"}"; do
    for scope in claude-code codex store; do
      entry="$(prune_path "$scope" "$name")"
      signature="$(entry_signature "$entry")"
      expect_prune_state "$scope" "$name" "$signature"
      if [ "$signature" != absent ]; then
        remove_entry "$entry"
        echo "REMOVED   deleted     $scope/$name"
      fi
    done
  done
}

report_unowned() {
  local agent="$1" root="$2" entry name
  [ -d "$root" ] || return

  shopt -s nullglob dotglob
  for entry in "$root"/*; do
    name="${entry##*/}"
    if ! is_owned "$name"; then
      echo "UNTOUCHED $agent $name (not owned by $SOURCE)"
    fi
  done
  shopt -u nullglob dotglob
}

if [ "${#owned[@]}" -eq 0 ] && [ "${#excluded[@]}" -eq 0 ]; then
  echo "no skills installed from $SOURCE — nothing to reconcile." >&2
else
  validate_roots
  for name in "${excluded[@]+"${excluded[@]}"}"; do
    canonical="$STORE/$name"
    for entry in "$CLAUDE_SKILLS/$name" "$CODEX_SKILLS/$name"; do
      if [ ! -L "$entry" ] && [ -e "$entry" ] && [ -e "$canonical" ] && [ "$entry" -ef "$canonical" ]; then
        echo "error: prune entry resolves to the canonical directory without being a symlink: $entry" >&2
        exit 2
      fi
    done
  done
  for name in "${owned[@]+"${owned[@]}"}"; do
    is_excluded "$name" && continue
    [ -d "$STORE/$name" ] || { echo "error: canonical skill is missing: $STORE/$name" >&2; exit 2; }
    for entry in "$CLAUDE_SKILLS/$name" "$CODEX_SKILLS/$name"; do
      if [ ! -L "$entry" ] && [ -e "$entry" ] && [ "$entry" -ef "$STORE/$name" ]; then
        echo "error: profile entry resolves to the canonical directory without being a symlink: $entry" >&2
        exit 2
      fi
    done
  done
  if $apply; then apply_pruned_paths; else preview_pruned_paths; fi
  for name in "${owned[@]+"${owned[@]}"}"; do
    is_excluded "$name" && continue
    reconcile_claude "$name"
    reconcile_codex "$name"
  done
fi

report_unowned "claude-code" "$CLAUDE_SKILLS"
report_unowned "codex      " "$CODEX_SKILLS"
