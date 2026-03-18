# AGENTS.md

Project-wide instructions for Codex and similar coding agents.

Codex must read and follow this file before making any changes.

## Source Of Truth

Shared repository rules live here and must be followed:

- `./.shared-agents/linting.md`

Reference the following shared skill documents when relevant:

- `./.shared-agents/skills/refactor-safely/SKILL.md`
- `./.shared-agents/skills/preserve-ui-behavior/SKILL.md`
- `./.shared-agents/skills/dry-simple-code/SKILL.md`
- `./.shared-agents/skills/comment-transformations/SKILL.md`

## Core Engineering Principles

### 1) Keep code DRY

- Reuse existing helpers, hooks, services, utils, types, constants, and UI components before creating new ones.
- Extract duplication only when it genuinely improves readability and maintainability.
- Do not create abstractions too early.
- Avoid “DRY at all costs”; duplicated code is acceptable temporarily if abstraction would make the code harder to understand.

### 2) Prefer the simplest working code

- The simplest correct solution is preferred over a clever one.
- Prefer straightforward control flow, readable names, and small functions.
- Minimize nesting.
- Prefer boring, maintainable code over over-engineered patterns.

### 3) Advanced logic must be explained with transformation comments

For code that is not immediately obvious, include short comments showing:

- the important input
- the transformation being applied
- the expected output shape or example output

Example:

```ts
// input: "hellohello"
const value = string.slice(0, 4);
// output: "hell"

// input: "hellohello"
const value2 = string.replace(/hello/g, "he");
// output: "hehe"
```

Rules:

- Only add these comments for logic that is non-obvious, compact, or easy to misread.
- Keep comments accurate and short.
- Do not add noisy comments for trivial code.

## Change Safety Rules

Do not break existing functionality, behavior, or UI.

When touching existing code, default to the smallest safe change.

Changes to old code are allowed when they clearly improve the codebase, such as:

- fixing a bug
- reducing code smell
- improving readability or maintainability
- improving performance without changing expected behavior
- improving accessibility
- improving UI/UX
- reducing duplication
- strengthening typing
- removing dead code
- simplifying overly complex code

### Guardrails for touching existing code

Before changing old code:

- understand current behavior first
- preserve public interfaces unless the task requires otherwise
- preserve API contracts
- preserve component props contracts
- preserve side effects that callers depend on
- preserve existing styling and interaction patterns unless intentionally improving them

### UI guardrails

Any UI change must:

- preserve layout intent unless improvement is required
- preserve responsive behavior
- preserve accessibility
- avoid visual regressions
- avoid changing copy, spacing, focus behavior, keyboard behavior, or loading states unless necessary

If a UI improvement is made:

- keep it minimal
- avoid unrelated redesign
- do not change multiple interaction patterns without need

## Refactoring Rules

Refactor only when one of these is true:

- the current code is buggy
- the current code is hard to understand
- the current code is unnecessarily duplicated
- the current code is risky to maintain
- the current code blocks a needed feature
- the current code causes UI/UX issues
- the current code has weak typing or unclear data flow
- the current code creates repeated defects

When refactoring:

- preserve behavior first
- prefer incremental refactors over sweeping rewrites
- keep diffs focused
- do not mix unrelated cleanup into feature work unless it is in the exact touched area and clearly safe

## Reuse-First Policy

Before creating anything new, search for:

- existing helper utilities
- shared types
- validation schemas
- data mappers
- API clients
- hooks
- UI primitives
- existing patterns already used in the repo

Prefer extending an existing file/module over adding a new one when responsibility remains clear.

## Validation Requirement

At the end of every coding task, follow:

- `./.shared-agents/linting.md`

Do not claim completion if changed code has known fixable lint, type, formatting, or test issues in the changed scope.

## Preferred Tooling

Use repository-native tooling first.

Well-known open-source tools commonly preferred when present in the repo:

- ESLint
- Prettier
- TypeScript
- Jest or Vitest
- Testing Library
- Husky
- lint-staged
- Knip

## Final Response Format For Coding Tasks

End with a compact validation summary including:

- commands run
- whether fixes were applied
- whether lint passed
- whether typecheck passed
- whether formatting passed
- any remaining issues, marked as either:
  - introduced by this task
  - pre-existing
