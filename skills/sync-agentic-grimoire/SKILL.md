---
name: sync-agentic-grimoire
description: Sync this machine's agentic-grimoire skills with the repo — update changed skills and prune ones deleted upstream.
disable-model-invocation: true
---

## Why this exists

`npx skills update --global` re-syncs *changed* skills but, at global scope, **does not prune**
skills deleted from the source repo — they linger as stale installs (upstream issue
[#415](https://github.com/vercel-labs/skills/issues/415)). This skill runs the update, then
does the prune the CLI lacks.

## Scope boundary (hard rule)

Prune **only** skills whose `~/.agents/.skill-lock.json` source is exactly
`healthier-vitamins/agentic-grimoire`. Skills from other sources (caveman, ask-matt, brand,
design, …) are never removed. Never run `npx skills remove --all`.

## How it works

- `npx skills update --global` handles the *changed* half (GitHub Tree SHA diff → re-`add`).
- `sync.sh` (this directory) computes the *prune set*, read-only: the skills installed from
  this repo (per `~/.agents/.skill-lock.json`) minus the repo's current `skills/` dirs (fetched live
  from the GitHub Contents API). It prints one name per line and **removes nothing** — the
  removal decision stays here, behind a confirm gate.
- If the GitHub fetch fails or is rate-limited, `sync.sh` exits non-zero and prunes nothing;
  do not guess a list — tell the user to retry.

## Steps

Let `DIR` be this skill's own directory (the folder holding this `SKILL.md`, i.e.
`~/.agents/skills/sync-agentic-grimoire`).

1. **Update changed skills:**
   ```sh
   npx skills update --global
   ```

2. **Compute the prune set:**
   ```sh
   bash "$DIR/sync.sh"
   ```
   - Non-zero exit → the fetch failed (offline / rate-limited). Report the stderr message and
     **stop** — nothing is pruned this run.
   - Empty output → nothing to prune; skip to step 5.

3. **Preview + confirm.** Show the user the prune set, each labelled
   "installed from agentic-grimoire, gone from repo", and ask for explicit confirmation
   **before** removing anything.

4. **Remove (only after the user confirms):**
   ```sh
   npx skills remove --global -a claude-code codex --yes <names-from-step-2>
   rm -rf ~/.agents/skills/<names-from-step-2>
   ```
   Pass only the names `sync.sh` printed. Other sources' skills stay installed.
   The `remove` clears the registry entry but **leaves the physical store dir**
   `~/.agents/skills/<name>`, which the next `npx skills` link pass re-links — so the
   explicit `rm -rf` is required to make the prune stick.

5. **Reminders** (no automatic invocation):
   - If `~/.claude-personal` or `~/.claude-sec` exists, tell the user to re-run
     `/link-agentic-grimoire-custom` — pruned skills leave dangling symlinks there that its
     re-run cleans up.
   - Tell the user to re-run `/setup-agentic-grimoire` if the guideline block changed upstream.

**Criterion:** every skill still installed from this source exists in the repo; other sources'
skills are untouched; a second run with no upstream changes reports nothing to prune (idempotent).
