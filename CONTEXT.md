# Context — agentic-grimoire

The project's ubiquitous language. A glossary only: terms and what they mean, no
implementation detail.

## Glossary

- **Skill** — a self-contained agent capability (a `SKILL.md` and its supporting files) that
  an agent can invoke. This repo's `skills/` directory is the source of the ones it publishes.

- **Store** — the single canonical location holding one real copy of each installed skill,
  at `~/.agents/skills/`. Owned by the `npx skills` CLI. Everything else points *into* it.

- **Memory file** — an agent's top-level instruction file: `~/.claude/CLAUDE.md` for Claude
  Code, `~/.codex/AGENTS.md` for Codex. Holds both the user's own content and the guideline block.

- **Guideline block** (a.k.a. **managed block**) — the passage of agentic-grimoire guidelines
  spliced into a memory file, delimited by the `AGENTIC-GRIMOIRE: MANAGED FILE` markers. The
  only region the guideline prompt edits; everything outside it belongs to the user and is
  never touched.
