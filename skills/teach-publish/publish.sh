#!/usr/bin/env bash
#
# teach-publish — sync a `teach` course folder to a private Cloudflare Pages site.
#
# This is the driver. SKILL.md is its man page; SETUP.md is the one-time runbook.
# Shape: a Template Method. main() runs a fixed sequence of named steps, in order,
# never reordered:
#
#   ensure_setup -> resolve_course -> sync_course -> ensure_course_index
#                -> regen_portal -> deploy
#
# Nothing personal lives in this file. Per-user state (the Cloudflare project name)
# lives in $CONFIG_FILE; the gate + allowed email live in the user's Cloudflare
# account. That separation is what makes the skill safe to share as-is.

set -euo pipefail

# --- configuration (all overridable via env, for tests + power users) ----------
CONFIG_FILE="${TEACH_PUBLISH_CONFIG:-${XDG_CONFIG_HOME:-$HOME/.config}/teach-publish/config}"
SITE_DIR="${TEACH_SITE_DIR:-$HOME/.teach-site}"
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- flags ---------------------------------------------------------------------
NO_DEPLOY=0
COURSE_DIR=""
SLUG=""
PROJECT_OVERRIDE=""

usage() {
  cat <<'EOF'
Usage: publish.sh [options]

  --course <dir>   Course folder to publish (default: cwd if it's a teach
                   workspace, else the sole folder under ./teach/).
  --slug <name>    URL subfolder name (default: the course folder's name).
  --project <name> Cloudflare Pages project name (overrides saved config).
  --no-deploy      Build the local staging site only; skip the wrangler upload.
  -h, --help       Show this help.

First run with deploy enabled walks you through one-time setup (see SETUP.md).
EOF
}

parse_args() {
  while [ $# -gt 0 ]; do
    case "$1" in
      --no-deploy) NO_DEPLOY=1 ;;
      --course)    COURSE_DIR="${2:?--course needs a path}"; shift ;;
      --slug)      SLUG="${2:?--slug needs a value}"; shift ;;
      --project)   PROJECT_OVERRIDE="${2:?--project needs a value}"; shift ;;
      -h|--help)   usage; exit 0 ;;
      *) echo "publish.sh: unknown option '$1'" >&2; usage >&2; exit 2 ;;
    esac
    shift
  done
}

say()  { printf '\033[1;36m▸ %s\033[0m\n' "$*"; }
warn() { printf '\033[1;33m! %s\033[0m\n' "$*" >&2; }
die()  { printf '\033[1;31m✗ %s\033[0m\n' "$*" >&2; exit 1; }

# --- 1. ensure_setup -----------------------------------------------------------
# First-run gate. Loads the saved config; if there's no project name yet AND we
# intend to deploy, bootstraps one (auth check -> prompt -> save -> gate hint).
# Idempotent: once the config exists this is silent.
ensure_setup() {
  mkdir -p "$(dirname "$CONFIG_FILE")" "$SITE_DIR"
  # shellcheck disable=SC1090
  [ -f "$CONFIG_FILE" ] && . "$CONFIG_FILE"
  [ -n "$PROJECT_OVERRIDE" ] && TEACH_PROJECT="$PROJECT_OVERRIDE"

  if [ -n "${TEACH_PROJECT:-}" ]; then
    return 0
  fi

  if [ "$NO_DEPLOY" -eq 1 ]; then
    warn "No project configured yet — fine for --no-deploy (local build only)."
    return 0
  fi

  # --- bootstrap: first deploy on this machine ---
  say "First-time setup (one time only — see $SKILL_DIR/SETUP.md)"

  if ! npx --yes wrangler whoami >/dev/null 2>&1; then
    die "Not logged in to Cloudflare. Run:  npx wrangler login
   (interactive browser auth — a human must do this), then re-run publish."
  fi

  if [ ! -t 0 ]; then
    die "No project configured and no TTY to prompt. Pass --project <name> or set
   TEACH_PROJECT=<name> in $CONFIG_FILE. (See SETUP.md.)"
  fi

  echo "Pick a globally-unique Cloudflare Pages project name (lowercase, e.g. 'my-teach')."
  echo "Your private site will live at https://<name>.pages.dev"
  printf 'Project name: '
  read -r TEACH_PROJECT
  [ -n "$TEACH_PROJECT" ] || die "Empty project name."

  printf 'TEACH_PROJECT=%s\n' "$TEACH_PROJECT" > "$CONFIG_FILE"
  say "Saved to $CONFIG_FILE"
  warn "After the first deploy, gate the site once in the Cloudflare dashboard"
  warn "(Workers & Pages -> $TEACH_PROJECT -> Settings -> Access). Steps: SETUP.md."
}

# --- 2. resolve_course ---------------------------------------------------------
# Decide which folder to publish and under what slug.
resolve_course() {
  if [ -z "$COURSE_DIR" ]; then
    if [ -d "lessons" ] && [ -f "MISSION.md" ]; then
      COURSE_DIR="."                      # cwd is itself a teach workspace
    elif [ -d "teach" ]; then
      # the sole course folder under ./teach/
      local matches=()
      while IFS= read -r d; do matches+=("$d"); done \
        < <(find teach -mindepth 1 -maxdepth 1 -type d | sort)
      [ "${#matches[@]}" -eq 0 ] && die "No course folders under ./teach/."
      [ "${#matches[@]}" -gt 1 ] && die "Multiple courses under ./teach/ — pass --course <dir>:
$(printf '   %s\n' "${matches[@]}")"
      COURSE_DIR="${matches[0]}"
    else
      die "No course found. Run from a teach workspace, or pass --course <dir>."
    fi
  fi

  [ -d "$COURSE_DIR" ] || die "Course dir not found: $COURSE_DIR"
  [ -d "$COURSE_DIR/lessons" ] || warn "No lessons/ in $COURSE_DIR — publishing anyway."

  if [ -z "$SLUG" ]; then
    SLUG="$(basename "$(cd "$COURSE_DIR" && pwd)")"
  fi
  say "Course: $COURSE_DIR  ->  slug: $SLUG"
}

# --- 3. sync_course ------------------------------------------------------------
# Mirror only the web parts of the course into the staging site. Internal teaching
# state (MISSION/NOTES/RESOURCES/learning-records) stays private and out of the
# published bundle.
sync_course() {
  local dest="$SITE_DIR/$SLUG"
  mkdir -p "$dest"
  rsync -a --delete \
    --exclude='.git' \
    --exclude='learning-records' \
    --exclude='MISSION.md' \
    --exclude='NOTES.md' \
    --exclude='RESOURCES.md' \
    "$COURSE_DIR"/ "$dest"/
  say "Synced -> $dest"
}

# --- 4. ensure_course_index ----------------------------------------------------
# If the course shipped no landing page, generate a TOC from its lessons.
ensure_course_index() {
  local dest="$SITE_DIR/$SLUG"
  if [ -f "$dest/index.html" ]; then
    return 0
  fi
  say "No course index.html — generating a fallback TOC."
  python3 "$SKILL_DIR/gen_portal.py" course "$dest"
}

# --- 5. regen_portal -----------------------------------------------------------
# Rebuild the top-level portal that lists every course on the site.
regen_portal() {
  python3 "$SKILL_DIR/gen_portal.py" portal "$SITE_DIR"
  say "Portal rebuilt -> $SITE_DIR/index.html"
}

# --- 6. deploy -----------------------------------------------------------------
deploy() {
  if [ "$NO_DEPLOY" -eq 1 ]; then
    say "--no-deploy: staged at $SITE_DIR (open $SITE_DIR/index.html). Skipping upload."
    return 0
  fi
  say "Deploying to Cloudflare Pages project: $TEACH_PROJECT"
  npx --yes wrangler pages deploy "$SITE_DIR" \
    --project-name "$TEACH_PROJECT" \
    --commit-dirty=true
  printf '\n\033[1;32m✓ Live: https://%s.pages.dev/%s/\033[0m\n' "$TEACH_PROJECT" "$SLUG"
}

main() {
  parse_args "$@"
  ensure_setup
  resolve_course
  sync_course
  ensure_course_index
  regen_portal
  deploy
}

main "$@"
