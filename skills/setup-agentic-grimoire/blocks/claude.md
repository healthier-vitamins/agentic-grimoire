# CLAUDE.md — agentic-grimoire guidelines

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## Validation

Before finishing coding work, run the validation commands that match the changed scope
(project scripts first, else the installed tool directly):

- JS/TS: `lint`, `typecheck`, `format:check`, `test` scripts — or `npx eslint .`, `npx tsc --noEmit`, `npx prettier --check .`
- Python: `uv run ruff check .`, `uv run ruff format --check .`, `uv run pyright`, `uv run pytest`

Do not finish with known safe-to-fix issues in the changed scope. Do not weaken rules or hide failures.

## Commits

Keep the default `Co-Authored-By` trailer that the harness adds — do not strip it.
Do **not** add the `Claude-Session` session-id/URL trailer to commit messages.
(Codex has no default co-author trailer, so it attaches nothing — that is expected.)

## Model Selection

For cost efficiency without quality loss, use the `opusplan` alias (`/model opus-plan`):
Opus plans and reviews, then auto-switches to Sonnet for execution within the same session.
Keep planning and final review on the top model and let Sonnet handle mechanical execution.
Do not downgrade further (e.g. Haiku) for non-trivial work — failed loops cost more than they save.

For codebase search, delegate to the built-in `Explore` agent rather than reading widely
inline, so the orchestrator's context stays clean.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked; no abstractions for single-use code.
- No "flexibility" that wasn't requested; no error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

- Don't "improve" adjacent code, comments, or formatting; don't refactor what isn't broken.
- Match existing style. If you notice unrelated dead code, mention it — don't delete it.
- Remove only the imports/variables YOUR changes made unused.
- The test: every changed line traces directly to the request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.** Transform tasks into verifiable goals
("fix the bug" → "write a failing test that reproduces it, then make it pass"). For
multi-step work, state a brief plan with a verify step per step.

## 5. Design Patterns

Reach for an established Gang-of-Four / architectural pattern before inventing structure —
don't build a bespoke solution a reviewer must reverse-engineer.

## Context7

Use the `context7` tool for library/framework/API documentation, setup, and configuration
steps. Do not rely on memory for library versions or APIs when verification is possible.

## Shell Tool Preferences

Prefer `fd` over `find` and `rg` over `grep`. If either is missing, say so and ask before installing.
