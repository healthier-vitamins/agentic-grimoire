# agentic-grimoire

Managed agent instruction files for Codex and Claude, plus an installer script that syncs them into a local home directory.

## What This Repo Does

This repo keeps two source instruction files:

- `.claude/CLAUDE.md`
- `.codex/AGENTS.md`

The installer script copies those docs into the expected locations in a target home directory and creates top-level aliases for tools that look for `~/.CLAUDE.md` or `~/.AGENT.md`.

## Install

Run the installer from the repo root:

```bash
scripts/install-agent-docs.sh
```

To install into a different home directory for testing:

```bash
AGENT_DOCS_HOME=/tmp/fake-home scripts/install-agent-docs.sh
```

To view usage:

```bash
scripts/install-agent-docs.sh --help
```

## Files It Installs

The script writes or updates these files under the target home directory:

- `~/.claude/CLAUDE.md`
- `~/.codex/AGENTS.md`
- `~/.CLAUDE.md`
- `~/.AGENT.md`

`~/.CLAUDE.md` is created as a symlink to `.claude/CLAUDE.md`, and `~/.AGENT.md` is created as a symlink to `.codex/AGENTS.md` when possible.

## Installer Behavior

The script is designed to be safe to rerun.

- It supports `macOS`, `Linux`, and `WSL`.
- If a target file does not exist, the script writes a managed file with the `AGENTIC-GRIMOIRE: MANAGED FILE` marker at the top.
- If a target file already contains that managed marker, the script replaces it with the latest generated content.
- If a target file exists but is unmanaged, the script preserves the existing content and appends a managed block at the bottom instead of overwriting the file.
- If that appended managed block already exists, the script updates just that block on later runs.
- If a target path is a conflicting symlink, the script leaves it unchanged and prints a warning.

The script prints a status line for each target. Current statuses are:

- `updated`
- `unchanged`
- `linked`
- `appended-with-warning`
- `skipped-conflicting-symlink`

## Shared Content

If a `.shared-agents/` directory exists in the repo, the installer merges those files into the generated output.

- `common/` content applies to both generated docs
- `claude/` content applies only to `CLAUDE.md`
- `codex/` content applies only to `AGENTS.md`

The merged section is wrapped in shared-content markers so the generated output is still traceable.

Current repo note: the source docs and installer reference `.shared-agents/`, but that directory is not present in this repo snapshot. The installer still works without it.

## Repo Layout

Key paths:

- `scripts/install-agent-docs.sh` - installer entrypoint
- `.claude/CLAUDE.md` - Claude source instructions
- `.codex/AGENTS.md` - Codex source instructions
- `.shared-agents/` - optional shared instruction fragments merged during install
- `skills/` - related skill markdown files kept in the repo

## Typical Workflow

1. Edit the source docs in `.claude/` or `.codex/`.
2. Optionally add shared fragments under `.shared-agents/`.
3. Run `scripts/install-agent-docs.sh`.
4. Review the printed statuses to confirm whether files were updated, linked, or preserved with an appended managed block.
