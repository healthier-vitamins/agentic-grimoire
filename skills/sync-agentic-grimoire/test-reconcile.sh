#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
TEST_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/agentic-grimoire-reconcile-test.XXXXXX")"
trap 'rm -rf -- "$TEST_ROOT"' EXIT

fail() {
  echo "FAIL: $1" >&2
  exit 1
}

owned_home="$TEST_ROOT/owned"
mkdir -p "$owned_home/.agents/skills/owned-skill" \
  "$owned_home/.claude/skills" "$owned_home/.codex/skills"
printf '%s\n' '{"skills":{"owned-skill":{"source":"healthier-vitamins/agentic-grimoire"}}}' \
  > "$owned_home/.agents/.skill-lock.json"
: > "$owned_home/exclusions"
output="$(HOME="$owned_home" bash "$DIR/reconcile.sh" --exclude-file "$owned_home/exclusions")"
case "$output" in
  *"LINK      claude-code owned-skill -> canonical store [state: absent]"*) ;;
  *) fail "empty exclusions did not preserve an owned skill" ;;
esac

unowned_home="$TEST_ROOT/unowned"
mkdir -p "$unowned_home/.agents" "$unowned_home/.claude/skills/unowned-skill" \
  "$unowned_home/.codex/skills"
printf '%s\n' '{"skills":{"unowned-skill":{"source":"another/source"}}}' \
  > "$unowned_home/.agents/.skill-lock.json"
output="$(HOME="$unowned_home" bash "$DIR/reconcile.sh" 2>&1)"
case "$output" in
  *"UNTOUCHED claude-code unowned-skill (not owned by healthier-vitamins/agentic-grimoire)"*) ;;
  *) fail "empty ownership did not report an unowned entry" ;;
esac

excluded_home="$TEST_ROOT/excluded"
mkdir -p "$excluded_home/.agents/skills" \
  "$excluded_home/.claude/skills" "$excluded_home/.codex/skills"
printf '%s\n' '{"skills":{"deleted-skill":{"source":"healthier-vitamins/agentic-grimoire"}}}' \
  > "$excluded_home/.agents/.skill-lock.json"
printf '%s\n' deleted-skill > "$excluded_home/exclusions"
output="$(HOME="$excluded_home" bash "$DIR/reconcile.sh" --exclude-file "$excluded_home/exclusions")"
expected=$'PRUNE\tstore\tdeleted-skill\tabsent\nPRUNE\tclaude-code\tdeleted-skill\tabsent\nPRUNE\tcodex\tdeleted-skill\tabsent'
[ "$output" = "$expected" ] || fail "non-empty exclusion did not produce all three PRUNE records"

echo "PASS: reconcile empty-array regression checks"
