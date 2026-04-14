# Linting And Validation Workflow

## Rule

Before finishing coding work, run the available validation commands that match the changed scope. Do not ignore failures in files or behavior you touched.

Fix safe issues you caused or touched when possible. Do not install new tools, weaken rules, or silently hide unresolved failures.

## Commands

Use project scripts first. If no script exists, use the installed tool directly.

JavaScript and TypeScript:

- Scripts: `npm/pnpm/yarn/bun run lint`, `typecheck`, `format:check`, and `test`
- Direct tools: `npx eslint .`, `npx tsc --noEmit`, `npx prettier --check .`

Python:

- Ruff: `uv run ruff check .`, `uv run ruff format --check .`
- Typecheck: `uv run pyright`
- Tests: `uv run pytest`
- Direct tools: `python -m ruff check .`, `python -m ruff format --check .`, `python -m pyright`, `python -m mypy .`, `python -m pytest`
