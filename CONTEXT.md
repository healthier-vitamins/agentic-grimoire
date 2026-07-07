# Context — agentic-grimoire

The project's ubiquitous language. A glossary only: terms and what they mean, no
implementation detail.

## Glossary

- **Skill** — a self-contained agent capability (a `SKILL.md` and its supporting files) that
  an agent can invoke. This repo's `skills/` directory is the source of the ones it publishes.

- **Store** — the single canonical location holding one real copy of each installed skill,
  at `~/.agents/skills/`. Owned by the `npx skills` CLI. Everything else points *into* it.

- **Profile** — one agent's configuration home. There are four: `~/.claude`, `~/.codex`,
  `~/.claude-personal`, `~/.claude-sec`. A profile's `skills/` are symlinks into the store,
  and its memory file carries the guideline block.

- **Conventional profile** — a profile the `npx skills` CLI recognises and links automatically:
  `~/.claude` (Claude Code) and `~/.codex` (Codex).

- **Custom profile** — a profile the CLI does not know about and cannot link:
  `~/.claude-personal` and `~/.claude-sec`. Covered by `link-agentic-grimoire-custom`.

- **Memory file** — a profile's top-level instruction file: `CLAUDE.md` for Claude profiles,
  `AGENTS.md` for Codex. Holds both the user's own content and the guideline block.

- **Guideline block** (a.k.a. **managed block**) — the passage of agentic-grimoire guidelines
  spliced into a memory file, delimited by the `AGENTIC-GRIMOIRE: MANAGED FILE` markers. The
  only region the setup skills own; everything outside it belongs to the user and is never
  touched.

- **Onboard** — the act of installing this repo's skills and guideline block into a machine's
  profiles: one `npx skills add` plus the setup slash command(s).
