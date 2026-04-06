# AGENTS.md

Project-wide instructions for Codex and similar coding agents.

Codex must read and follow this file before making changes.

## Source Of Truth

Shared repository rules live here and must be followed:

- `./.shared-agents/linting.md`
- `./.shared-agents/common/skills/coexistance/SKILL.md`

## Core Engineering Principles

### Reuse first

- Reuse existing helpers, hooks, services, utils, types, constants, and UI components before creating new ones.
- Search for existing validators, mappers, API clients, hooks, and shared UI patterns before adding code.
- Prefer extending an existing module over adding a new one when responsibility stays clear.
- Extract helpers only when reuse is real and naming is obvious.
- If an abstraction makes the code harder to read, keep the logic inline.

### Keep code DRY and simple

- Prefer the simplest correct solution over a clever one.
- Use straightforward control flow, readable names, and small focused functions.
- Minimize nesting and avoid compressed one-liners when branching would be clearer.
- Duplicated code is acceptable temporarily if abstraction would reduce clarity.
- Avoid generic utilities or new patterns unless the repo clearly needs them.

### Comment dense transformations

For non-obvious logic, add short comments that show the input and output shape.

```ts
// input: "alpha,beta,gamma"
const firstTwo = value.split(",").slice(0, 2);
// output: ["alpha", "beta"]
```

Rules:

- Add these comments only for dense string/array/object transforms, regex logic, parsing, mapping, filtering, or normalization.
- Keep comments short, accurate, and specific to the tricky part.
- Do not add comments for obvious code.

## Change Safety Rules

Do not break existing functionality, behavior, or UI.

- Default to the smallest safe change.
- Understand current behavior before editing old code.
- Preserve public interfaces unless the task explicitly requires change.
- Preserve API contracts, component prop contracts, and side effects callers depend on.
- Keep data flow explicit and keep side effects where callers expect them.
- Do not mix unrelated cleanup into the same diff.

Changes to existing code are encouraged when they clearly improve the codebase, such as:

- fixing bugs
- reducing duplication or code smell
- improving readability, maintainability, or typing
- simplifying risky or confusing logic
- improving accessibility or UI/UX
- removing dead code
- improving performance without changing expected behavior

## Refactoring Rules

Refactor only when the current code is buggy, duplicated, confusing, risky, or blocking necessary work.

When refactoring:

1. Identify current behavior first.
2. Identify what is duplicated, fragile, confusing, or risky.
3. Refactor only the touched area unless expansion is necessary.
4. Preserve behavior with tests or strong local reasoning.
5. Re-run validation after the change.

Avoid:

- sweeping rewrites
- hidden behavior changes
- silent API contract changes
- opportunistic redesign

## UI Guardrails

Any UI change must:

- preserve layout intent unless an improvement is required
- preserve responsive behavior
- preserve accessibility and keyboard interaction
- preserve focus behavior
- preserve empty, loading, success, and error states
- avoid unrelated changes to copy, spacing, alignment, or interaction patterns

Safe UI improvements include:

- fixing broken alignment
- improving accessibility labels
- simplifying duplicated render branches
- reducing rerenders without changing behavior
- improving disabled or loading state consistency

Before finishing a UI change:

- compare old and new rendered states mentally or with tests
- verify no unrelated visual regression was introduced

## Validation Requirement

At the end of every coding task, follow:

- `./.shared-agents/linting.md`

Do not claim completion if changed code has known fixable lint, type, formatting, or test issues in the changed scope.

## Preferred Tooling

Use repository-native tooling first. Prefer these well-known tools when already present in the repo:

- ESLint
- Prettier
- TypeScript
- Jest or Vitest
- Testing Library
- Husky
- lint-staged
- Knip

## Context7 For Library And API Guidance

Context7 is the default source for library and framework documentation.

- Use the `context7` tool when you need library or API documentation.
- Use the `context7` tool when you need code generation, setup instructions, or configuration steps.
- Do not rely on memory for library versions or APIs when verification is needed.

## Shell Search Tools

Prefer modern CLI tools for searches:

- Use `fd` instead of `find`.
- Use `rg` instead of `grep`.

If either tool is missing, ask the user before running an install command.

## Final Response Format For Coding Tasks

End with a compact validation summary including:

- commands run
- whether fixes were applied
- whether lint passed
- whether typecheck passed
- whether formatting passed
- any remaining issues, marked as `introduced by this task` or `pre-existing`
