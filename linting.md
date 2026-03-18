# Linting And Validation Workflow

This repository requires validation at the end of every coding task.

## Goal

Do not finish a coding task with known lint errors in the changed scope if they can be fixed safely in the same session.

## Validation Order

Prefer project-defined scripts first. Start narrow when possible, then broaden if needed.

Typical order:

1. Run targeted lint, typecheck, and test commands for the changed files or packages.
2. Run repo-level lint.
3. Run repo-level typecheck.
4. Run formatting checks or formatting commands if the repo enforces formatting.

## Preferred Commands

Use whichever commands exist in this repository.

### Lint

- `npm run lint`
- `pnpm lint`
- `yarn lint`
- `bun run lint`
- `npx eslint . --fix`

### Typecheck

- `npm run typecheck`
- `pnpm typecheck`
- `yarn typecheck`
- `bun run typecheck`
- `npx tsc --noEmit`

### Format

- `npm run format:check`
- `npm run format`
- `pnpm format:check`
- `pnpm format`
- `yarn format:check`
- `yarn format`
- `bun run format:check`
- `bun run format`
- `npx prettier --check .`
- `npx prettier --write .`

## Auto-Fix Policy

Apply safe auto-fixes when clearly appropriate:

- formatter fixes
- ESLint auto-fixes
- import ordering fixes
- removal of unused imports or variables when behavior is unchanged

Do not weaken lint rules, remove useful checks, or bypass failing validation just to make the task pass unless explicitly requested.

## Manual Fix Expectations

When validation reveals non-auto-fixable issues in files you touched, fix them before finishing when reasonable.

Examples:

- missing types
- unsafe `any`
- unused code introduced by the change
- React hook dependency issues
- accessibility regressions
- broken tests caused by the change

If there are unrelated pre-existing failures outside the task scope, do not silently ignore them. Call them out clearly.

## Final Response Requirements

For code-editing tasks, end with a compact validation summary that includes:

- commands run
- whether fixes were applied
- whether lint passed
- whether typecheck passed
- whether formatting passed
-
