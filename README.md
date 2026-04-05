# agentic-grimoire

Managed agent instruction files for Codex and Claude, plus a Node installer that syncs them into the local home directory.

## What This Repo Does

This repo keeps two source instruction files:

- `.claude/CLAUDE.md`
- `.codex/AGENTS.md`

The installer copies those docs into the expected locations in the current user's home directory.

## Install

Run the installer from the repo root:

```bash
node scripts/install-agent-docs.js
```

To view usage:

```bash
node scripts/install-agent-docs.js --help
```

## Files It Installs

The installer writes or updates these files under the current user's home directory:

- `~/.claude/CLAUDE.md`
- `~/.codex/AGENTS.md`

## Installer Behavior

The installer is designed to be safe to rerun.

- It supports `macOS`, `Linux`, and `WSL`.
- If a target file does not exist, the installer writes a managed file with the `AGENTIC-GRIMOIRE: MANAGED FILE` marker at the top.
- If a target file already contains that managed marker, the script replaces it with the latest generated content.
- If a target file exists but is unmanaged, the installer preserves the existing content and appends one managed section at the bottom instead of overwriting the file.
- If that appended managed section already exists, the installer updates just that section on later runs instead of adding it twice.
- If a target path is a conflicting symlink, the script leaves it unchanged and prints a warning.

Appended unmanaged-file sections are clearly delimited with ASCII markers so the repo-managed portion is easy to identify.

The installer prints a status line for each target. Current statuses are:

- `updated`
- `unchanged`
- `appended-with-warning`
- `skipped-conflicting-symlink`

## Shared Content

If a `.shared-agents/` directory exists in the repo, the installer merges those files into the generated output.

- `common/` content applies to both generated docs
- `claude/` content applies only to `CLAUDE.md`
- `codex/` content applies only to `AGENTS.md`

The merged section is wrapped in shared-content markers so the generated output is still traceable.

## Repo Layout

Key paths:

- `scripts/install-agent-docs.js` - installer entrypoint
- `.claude/CLAUDE.md` - Claude source instructions
- `.codex/AGENTS.md` - Codex source instructions
- `.shared-agents/` - optional shared instruction fragments merged during install
- `skills/` - related skill markdown files kept in the repo

## Typical Workflow

1. Edit the source docs in `.claude/` or `.codex/`.
2. Optionally add shared fragments under `.shared-agents/`.
3. Run `node scripts/install-agent-docs.js`.
4. Review the printed statuses to confirm whether files were updated or preserved with an appended managed section.
