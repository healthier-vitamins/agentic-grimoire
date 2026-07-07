#!/usr/bin/env bash
# link.sh [profile ...]
#
# Mirror the central skill store (~/.agents/skills) into custom Claude profiles that
# the `npx skills` CLI can't reach. Defaults to .claude-personal and .claude-sec.
#
# Safety rules (ported from the retired sync_agent_docs.py):
#   - create relative symlinks into the store
#   - NEVER destroy a real dir the user placed there (skip it, warn)
#   - leave unrelated symlinks (not pointing into the store) untouched
#   - prune only store symlinks whose target no longer exists
set -euo pipefail
shopt -s nullglob

store="$HOME/.agents/skills"
if [ ! -d "$store" ]; then
  echo "error: store $store not found — run 'npx skills add healthier-vitamins/agentic-grimoire --global' first." >&2
  exit 1
fi

if [ "$#" -gt 0 ]; then profiles=("$@"); else profiles=(.claude-personal .claude-sec); fi

for profile in "${profiles[@]}"; do
  dst="$HOME/$profile/skills"
  mkdir -p "$dst"

  for skill in "$store"/*/; do
    name="$(basename "$skill")"
    case "$name" in .*) continue ;; esac
    link="$dst/$name"
    target="../../.agents/skills/$name"   # relative: ~/.<profile>/skills -> ~/.agents/skills

    if [ -L "$link" ]; then
      case "$(readlink "$link")" in
        *".agents/skills/"*) ln -sfn "$target" "$link"; echo "linked   $link" ;;
        *)                   echo "skip     $link (unmanaged symlink)" ;;
      esac
    elif [ -e "$link" ]; then
      echo "skip     $link (real dir preserved)"
    else
      ln -s "$target" "$link"; echo "linked   $link"
    fi
  done

  # prune dangling store links
  for link in "$dst"/*; do
    [ -L "$link" ] && [ ! -e "$link" ] || continue
    case "$(readlink "$link")" in
      *".agents/skills/"*) rm "$link"; echo "pruned   $link" ;;
    esac
  done
done
