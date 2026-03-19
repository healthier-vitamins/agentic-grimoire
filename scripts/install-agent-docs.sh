#!/usr/bin/env bash
set -euo pipefail

MANAGED_FILE_MARKER='<!-- AGENTIC-GRIMOIRE: MANAGED FILE -->'
BEGIN_SHARED_BLOCK='<!-- BEGIN AGENTIC-GRIMOIRE SHARED CONTENT -->'
END_SHARED_BLOCK='<!-- END AGENTIC-GRIMOIRE SHARED CONTENT -->'
BEGIN_INSTALL_BLOCK='<!-- BEGIN AGENTIC-GRIMOIRE MANAGED BLOCK -->'
END_INSTALL_BLOCK='<!-- END AGENTIC-GRIMOIRE MANAGED BLOCK -->'

SCRIPT_DIR=$(
  cd -- "$(dirname "${BASH_SOURCE[0]}")" && pwd
)
REPO_ROOT=$(
  cd -- "${SCRIPT_DIR}/.." && pwd
)
TARGET_HOME=${AGENT_DOCS_HOME:-${HOME:-}}

CLAUDE_SOURCE="${REPO_ROOT}/.claude/CLAUDE.md"
CODEX_SOURCE="${REPO_ROOT}/.codex/AGENTS.md"
SHARED_DIR="${REPO_ROOT}/.shared-agents"

TMP_DIR=$(mktemp -d)
trap 'rm -rf "${TMP_DIR}"' EXIT

warn() {
  printf 'WARNING: %s\n' "$*" >&2
}

die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

status() {
  printf '%s: %s\n' "$1" "$2"
}

usage() {
  cat <<'EOF'
Usage: scripts/install-agent-docs.sh

Installs repo agent docs into the current device home directory.

Optional environment override:
  AGENT_DOCS_HOME=/tmp/fake-home scripts/install-agent-docs.sh
EOF
}

detect_platform() {
  local uname_s

  uname_s=$(uname -s)
  case "${uname_s}" in
    Darwin)
      printf 'macOS\n'
      ;;
    Linux)
      if grep -qi microsoft /proc/version 2>/dev/null || grep -qi microsoft /proc/sys/kernel/osrelease 2>/dev/null; then
        printf 'WSL\n'
      else
        printf 'Linux\n'
      fi
      ;;
    *)
      die "unsupported platform '${uname_s}'. Only Linux, macOS, and WSL are supported."
      ;;
  esac
}

ensure_prereqs() {
  [[ -n "${TARGET_HOME}" ]] || die "HOME is not set and AGENT_DOCS_HOME was not provided."
  [[ -f "${CLAUDE_SOURCE}" ]] || die "missing source file: ${CLAUDE_SOURCE}"
  [[ -f "${CODEX_SOURCE}" ]] || die "missing source file: ${CODEX_SOURCE}"
}

ensure_parent_dir() {
  mkdir -p -- "$(dirname "$1")"
}

applies_to_kind() {
  local rel_path=$1
  local kind=$2

  case "${rel_path}" in
    claude/*)
      [[ "${kind}" == "claude" ]]
      ;;
    codex/*)
      [[ "${kind}" == "codex" ]]
      ;;
    common/*)
      return 0
      ;;
    *)
      return 0
      ;;
  esac
}

build_shared_block() {
  local kind=$1
  local out_file=$2
  local shared_found=0
  local file
  local rel_path

  : > "${out_file}"
  [[ -d "${SHARED_DIR}" ]] || return 1

  while IFS= read -r file; do
    rel_path=${file#"${SHARED_DIR}/"}
    applies_to_kind "${rel_path}" "${kind}" || continue

    if (( shared_found == 0 )); then
      printf '%s\n' "${BEGIN_SHARED_BLOCK}" >> "${out_file}"
      printf '<!-- generated from .shared-agents -->\n' >> "${out_file}"
      shared_found=1
    fi

    printf '\n## Shared Instructions: `%s`\n\n' "${rel_path}" >> "${out_file}"
    cat "${file}" >> "${out_file}"

    if [[ $(tail -c 1 "${file}" 2>/dev/null || true) != "" ]]; then
      printf '\n' >> "${out_file}"
    fi
  done < <(find "${SHARED_DIR}" -type f | sort)

  (( shared_found == 1 )) || return 1
  printf '\n%s\n' "${END_SHARED_BLOCK}" >> "${out_file}"
}

build_desired_doc() {
  local kind=$1
  local source_file=$2
  local out_file=$3
  local shared_file="${TMP_DIR}/${kind}-shared.md"

  cat "${source_file}" > "${out_file}"

  if [[ $(tail -c 1 "${source_file}" 2>/dev/null || true) != "" ]]; then
    printf '\n' >> "${out_file}"
  fi

  if build_shared_block "${kind}" "${shared_file}"; then
    printf '\n' >> "${out_file}"
    cat "${shared_file}" >> "${out_file}"
  fi
}

build_managed_file() {
  local desired_file=$1
  local out_file=$2

  {
    printf '%s\n\n' "${MANAGED_FILE_MARKER}"
    cat "${desired_file}"
  } > "${out_file}"
}

build_append_block() {
  local desired_file=$1
  local intended_target=$2
  local out_file=$3

  {
    printf '%s\n' "${BEGIN_INSTALL_BLOCK}"
    printf '<!-- intended target: %s -->\n\n' "${intended_target}"
    cat "${desired_file}"
    printf '\n%s\n' "${END_INSTALL_BLOCK}"
  } > "${out_file}"
}

upsert_block() {
  local target_file=$1
  local block_file=$2
  local out_file=$3

  awk -v begin="${BEGIN_INSTALL_BLOCK}" -v end="${END_INSTALL_BLOCK}" '
    $0 == begin { in_block = 1; next }
    $0 == end { in_block = 0; next }
    !in_block { print }
  ' "${target_file}" > "${out_file}"

  if [[ -s "${out_file}" ]] && [[ $(tail -c 1 "${out_file}" 2>/dev/null || true) != "" ]]; then
    printf '\n' >> "${out_file}"
  fi

  cat "${block_file}" >> "${out_file}"
}

sync_regular_file() {
  local target_file=$1
  local desired_file=$2
  local label=$3
  local managed_file="${TMP_DIR}/managed-$(basename "${target_file}").tmp"
  local append_block="${TMP_DIR}/append-$(basename "${target_file}").tmp"
  local candidate="${TMP_DIR}/candidate-$(basename "${target_file}").tmp"

  ensure_parent_dir "${target_file}"
  build_managed_file "${desired_file}" "${managed_file}"

  if [[ ! -e "${target_file}" && ! -L "${target_file}" ]]; then
    cp "${managed_file}" "${target_file}"
    status "${label}" "updated"
    return 0
  fi

  if [[ -L "${target_file}" ]]; then
    if cmp -s "${target_file}" "${desired_file}"; then
      status "${label}" "unchanged"
      return 0
    fi

    warn "${target_file} is a symlink to an unmanaged target. Leaving it unchanged."
    status "${label}" "skipped-conflicting-symlink"
    return 0
  fi

  if cmp -s "${target_file}" "${managed_file}" || cmp -s "${target_file}" "${desired_file}"; then
    status "${label}" "unchanged"
    return 0
  fi

  if grep -Fxq "${MANAGED_FILE_MARKER}" "${target_file}"; then
    cp "${managed_file}" "${target_file}"
    status "${label}" "updated"
    return 0
  fi

  build_append_block "${desired_file}" "${target_file}" "${append_block}"

  if grep -Fxq "${BEGIN_INSTALL_BLOCK}" "${target_file}" && grep -Fxq "${END_INSTALL_BLOCK}" "${target_file}"; then
    upsert_block "${target_file}" "${append_block}" "${candidate}"

    if cmp -s "${target_file}" "${candidate}"; then
      status "${label}" "unchanged"
      return 0
    fi

    cp "${candidate}" "${target_file}"
    status "${label}" "updated"
    return 0
  fi

  warn "${target_file} already existed. Preserved original content and appended a managed block at the bottom."
  if [[ $(tail -c 1 "${target_file}" 2>/dev/null || true) != "" ]]; then
    printf '\n' >> "${target_file}"
  fi
  cat "${append_block}" >> "${target_file}"
  status "${label}" "appended-with-warning"
}

sync_alias() {
  local alias_path=$1
  local link_target=$2
  local desired_file=$3
  local label=$4

  ensure_parent_dir "${alias_path}"

  if [[ -L "${alias_path}" ]]; then
    if [[ $(readlink "${alias_path}") == "${link_target}" ]]; then
      status "${label}" "linked"
      return 0
    fi

    warn "${alias_path} is a conflicting symlink. Leaving it unchanged."
    status "${label}" "skipped-conflicting-symlink"
    return 0
  fi

  if [[ ! -e "${alias_path}" ]]; then
    ln -s "${link_target}" "${alias_path}"
    status "${label}" "linked"
    return 0
  fi

  sync_regular_file "${alias_path}" "${desired_file}" "${label}"
}

main() {
  local platform
  local claude_desired="${TMP_DIR}/claude-desired.md"
  local codex_desired="${TMP_DIR}/codex-desired.md"
  local home_claude_dir="${TARGET_HOME}/.claude"
  local home_codex_dir="${TARGET_HOME}/.codex"
  local home_claude_file="${home_claude_dir}/CLAUDE.md"
  local home_codex_file="${home_codex_dir}/AGENTS.md"

  if [[ ${1:-} == "--help" ]]; then
    usage
    exit 0
  fi

  platform=$(detect_platform)
  ensure_prereqs

  build_desired_doc "claude" "${CLAUDE_SOURCE}" "${claude_desired}"
  build_desired_doc "codex" "${CODEX_SOURCE}" "${codex_desired}"

  printf 'Platform: %s\n' "${platform}"
  printf 'Target home: %s\n' "${TARGET_HOME}"

  sync_regular_file "${home_claude_file}" "${claude_desired}" "~/.claude/CLAUDE.md"
  sync_regular_file "${home_codex_file}" "${codex_desired}" "~/.codex/AGENTS.md"
  sync_alias "${TARGET_HOME}/.CLAUDE.md" ".claude/CLAUDE.md" "${claude_desired}" "~/.CLAUDE.md"
  sync_alias "${TARGET_HOME}/.AGENT.md" ".codex/AGENTS.md" "${codex_desired}" "~/.AGENT.md"
}

main "$@"
