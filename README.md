# agentic-grimoire

A collection of agent **skills** plus the guideline block they install into your
Claude Code and Codex config. Onboarding is one `npx` line and one or two slash commands —
no Makefile, no build step.

## Onboard

```sh
# 1. Install the skills into the central store (~/.agents/skills) and symlink them
#    into the conventional profiles (Claude Code + Codex).
npx skills add healthier-vitamins/agentic-grimoire --global -a claude-code codex --yes

# 2. Splice the guideline block into ~/.claude/CLAUDE.md AND ~/.codex/AGENTS.md
#    (append-only, idempotent — your existing content is preserved).
/setup-agentic-grimoire

# 3. Optional: extend to the custom profiles ~/.claude-personal and ~/.claude-sec
#    (symlink the store into them + splice their CLAUDE.md).
/link-agentic-grimoire-custom
```

Steps 2 and 3 are slash commands you run **inside** Claude Code — they ship as skills, so
step 1 installs them. The first run is worth doing interactively so you can eyeball the diff
into your own config; after that it's safe to re-run (idempotent).

## How it splits responsibility

- **`npx skills`** ([vercel-labs/skills](https://github.com/vercel-labs/skills)) owns the
  skills: it installs a canonical copy into the store `~/.agents/skills/` and symlinks it
  into every *detected* agent (`~/.claude/skills/`, `~/.codex/skills/`). It never touches
  `CLAUDE.md`/`AGENTS.md`, and it can't see custom profile dirs.
- **`setup-agentic-grimoire`** fills the first gap — it splices the guideline block between
  `<!-- AGENTIC-GRIMOIRE: MANAGED FILE -->` markers in `~/.claude/CLAUDE.md` and
  `~/.codex/AGENTS.md`. A re-run replaces only that block; everything you wrote outside it
  survives.
- **`link-agentic-grimoire-custom`** fills the second — it symlinks the store into
  `~/.claude-personal` and `~/.claude-sec` (preserving any real skill dir you placed there,
  pruning only dead store links) and splices their `CLAUDE.md` the same way.

## Updating

Edit a skill or the guideline blocks here → commit → push → `npx skills update --global`,
then re-run `/setup-agentic-grimoire` (and `/link-agentic-grimoire-custom`) to refresh the
managed block. Authors and consumers onboard the same way.

## Repo layout

- `skills/` — the skills, incl. `setup-agentic-grimoire/` (the guideline blocks +
  `splice.sh`) and `link-agentic-grimoire-custom/` (`link.sh`).
- `CLAUDE.md` / `AGENTS.md` — this repo's *own* dev guidance (no longer synced anywhere).
- `docs/adr/` — architecture decision records.

See [`docs/adr/0002-npx-skills-onboarding.md`](docs/adr/0002-npx-skills-onboarding.md) for
why the old `make`/Python sync engine was retired, and [`CONTEXT.md`](CONTEXT.md) for the
project's vocabulary.
