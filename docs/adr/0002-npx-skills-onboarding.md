# 2. Onboard via `npx skills` + agent-driven setup skills

Date: 2026-07-08

## Status

Accepted. Supersedes [0001](0001-central-skill-store-symlinks.md).

## Context

ADR 0001 built a 426-line Python engine (`scripts/sync_agent_docs.py`), a `Makefile`, and
`SYNC.md` to own the skill store and symlink topology for all four profiles. Most of that code
existed to *fight* the [`npx skills`](https://github.com/vercel-labs/skills) CLI's local-path
behaviour: `add ./skills` copies skills into the store and leaves them stale, so the engine
re-refreshed the store from the repo on every run. Maintaining and running this was painful,
and the whole apparatus reimplemented what the CLI already does for **github-sourced** skills.

Two responsibilities the CLI genuinely does *not* cover remained:

1. It never edits `CLAUDE.md` / `AGENTS.md`.
2. It has no concept of the custom profiles `~/.claude-personal` / `~/.claude-sec`.

## Decision

Retire the engine. Distribute skills the way the CLI is designed for — **github-sourced** —
and cover the two gaps with skills that ship *in* the package:

- **Onboard:** `npx skills add healthier-vitamins/agentic-grimoire --global -a claude-code codex --yes`.
  Because the source is a GitHub repo (not a local path), the CLI symlinks skills from the store
  cleanly — the staleness ADR 0001 fought does not arise. Authors publish by push; consumers and
  authors onboard identically. (Trade-off: local edits are live only after commit + push +
  `npx skills update` — no live working-tree editing.)
- **`setup-agentic-grimoire`** splices a canonical, bundled guideline block between the
  `<!-- AGENTIC-GRIMOIRE: MANAGED FILE -->` markers in `~/.claude/CLAUDE.md` and
  `~/.codex/AGENTS.md`. A bundled `splice.sh` does it deterministically: replace only the marked
  region, preserve all other content, no-op if unchanged. Reusing the marker convention from the
  retired engine.
- **`link-agentic-grimoire-custom`** symlinks the store into the custom profiles (bundled
  `link.sh`, carrying forward ADR 0001's safety rules: relative symlinks, preserve a divergent
  real dir, prune only dangling store links) and splices their `CLAUDE.md`.

Agent-definition syncing (`claude/agents/`, `codex/agents/` → profile `agents/` dirs) is
**dropped** — the CLI does not do it and it is out of scope for this onboarding.

## Consequences

- No `Makefile` and no Python to maintain; onboarding is one `npx` line plus two slash commands.
- The determinism ADR 0001 got from Python now lives in two small bundled shell scripts
  (`splice.sh`, `link.sh`), verified against the same guarantees (idempotency, content
  preservation, divergent-dir safety) the old `test_sync_skills.py` asserted.
- Skills no longer edit live from the working tree; the edit→push→update loop replaces it. This
  is the accepted cost of dropping the local-path copy dance.
- Agent definitions are no longer installed; `CLAUDE.md`/`AGENTS.md` references to specific
  `executor`/`explorer` subagents were trimmed to match.
