# CLAUDE.md

Persistent project instructions for Claude Code.

Follow this file before editing code, running validations, or proposing refactors.

## Shared Rules

Shared repository rules live here:

- `./.shared-agents/linting.md`
- `./.shared-agents/common/skills/coexistance/SKILL.md`

## Working Style

### Reuse first

- Check for existing helpers, hooks, services, types, parsers, validators, constants, and UI components before creating new ones.
- Reuse and extend established repo patterns where appropriate.
- Prefer extending an existing module over adding a new one when responsibility stays clear.
- Extract helpers only when the reuse is real and the name is obvious.
- If abstraction makes the code harder to follow, keep the logic inline.

### Keep code DRY and simple

- Prefer the simplest correct solution.
- Avoid clever abstractions unless they are clearly justified.
- Write code that a junior engineer can trace confidently.
- Prefer focused functions and readable branching over compact one-liners.
- Do not introduce generic utilities or new patterns too early.

### Comment non-obvious transformations

For advanced or dense logic, add short comments that show sample input and expected output.

```ts
// input: "a,b,c,d"
const items = value.split(",").slice(0, 2);
// output: ["a", "b"]
```

Use these comments for dense transforms, regex logic, parsing, mapping, filtering, or normalization. Do not add them for obvious code.

## Safety Rules For Existing Code

Assume existing behavior is relied upon unless proven otherwise.

Do not break:

- existing functionality
- API behavior
- component contracts
- data flow
- side effects callers rely on
- UI behavior
- accessibility
- responsive behavior

Only touch old code when it is a real improvement, including:

- bug fixes
- code smell reduction
- readability or maintainability improvements
- safe simplification
- safer typing
- accessibility or UI/UX improvements
- dead code removal
- duplicated logic reduction
- performance improvements that preserve behavior

Guardrails:

- make the smallest safe change by default
- understand current behavior before editing
- keep data flow explicit
- keep side effects where callers expect them
- do not mix unrelated cleanup into the same diff

## Refactor Policy

Prefer narrow, safe refactors.

Refactor process:

1. Identify current behavior first.
2. Identify what is duplicated, confusing, fragile, or risky.
3. Refactor only the touched area unless expansion is necessary.
4. Preserve behavior with tests or strong local reasoning.
5. Re-run validation after the change.

Good refactors:

- remove duplication in the touched area
- rename confusing variables or functions
- isolate side effects
- simplify conditionals
- replace fragile logic with explicit logic
- improve typings
- break large functions into clearer pieces

Avoid:

- broad rewrites without strong need
- hidden behavior changes
- silent API contract changes
- changing unrelated files
- opportunistic redesign

## UI Protection Rules

When editing frontend code:

- preserve current layout intent unless improving it
- preserve spacing, copy, and alignment unless change is deliberate
- preserve loading, empty, error, hover, focus, success, and disabled states
- preserve keyboard interactions and accessibility behavior
- preserve responsive behavior
- verify no unrelated visual regressions are introduced

If improving UI/UX:

- make the smallest improvement that solves the problem
- keep styling consistent with the existing codebase
- avoid unrelated redesign

## Validation

Before finishing any code task, follow:

- `./.shared-agents/linting.md`

Do not finish with known safe-to-fix issues in the changed scope.

## Preferred Open Source Tooling

When these tools already exist in the repo, prefer them over introducing alternatives:

- ESLint
- Prettier
- TypeScript
- Jest
- Vitest
- Testing Library
- Playwright
- Husky
- lint-staged
- Knip

## Context7

Context7 is the default source for library and framework documentation.

- Use the `context7` tool when you need library or API documentation.
- Use the `context7` tool when you need code generation, setup instructions, or configuration steps.
- Do not rely on memory for library versions or APIs when verification is needed.

## Shell Tool Preferences

Prefer modern CLI search tools for efficiency:

- Use `fd` instead of `find`.
- Use `rg` instead of `grep`.

If either tool is missing, inform the user and ask before running an install command.

## Expected End-Of-Task Summary

For code tasks, end with:

- commands run
- fixes applied
- lint status
- typecheck status
- formatting status
- remaining issues marked as `introduced by this task` or `pre-existing`
