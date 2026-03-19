# CLAUDE.md

Persistent project instructions for Claude Code.

Follow this file before editing code, running validations, or proposing refactors.

## Shared Rules

Shared repository rules live here:

- `~/.shared-agents/linting.md`

Relevant shared skills:

- `~/.shared-agents/skills/refactor-safely/SKILL.md`
- `~/.shared-agents/skills/preserve-ui-behavior/SKILL.md`
- `~/.shared-agents/skills/dry-simple-code/SKILL.md`
- `~/.shared-agents/skills/comment-transformations/SKILL.md`

## Working Style

### Keep code DRY

- Always look for existing helpers, hooks, services, types, utilities, and UI components before creating new ones.
- Reuse and extend existing patterns where appropriate.
- Only extract abstractions when they make the code easier to understand and maintain.

### Simplicity first

- Prefer the simplest correct solution.
- Avoid clever abstractions unless they are clearly justified.
- Write code that a junior engineer can trace confidently.

### Comment non-obvious transformations

For advanced or dense logic, add short comments that show:

- sample input
- transformation
- expected output

Example:

```ts
// input: "hellohello"
const value = string.slice(0, 4);
// output: "hell"

// input: "a,b,c,d"
const items = value.split(",").slice(0, 2);
// output: ["a", "b"]
```

Do not add unnecessary comments for obvious code.

## Safety Rules For Existing Code

Assume existing behavior is relied upon unless proven otherwise.

Do not break:

- existing functionality
- API behavior
- component contracts
- data flow
- UI behavior
- accessibility
- responsive behavior

Only touch old code when it is a real improvement, including:

- bug fixes
- code smell reduction
- readability improvements
- safe simplification
- safer typing
- accessibility improvements
- UI/UX improvements
- dead code removal
- duplicated logic reduction
- performance improvements that preserve behavior

## Refactor Policy

Prefer narrow, safe refactors.

Good refactors:

- remove duplication in the touched area
- rename confusing variables/functions
- isolate side effects
- simplify conditionals
- replace fragile logic with explicit logic
- improve typings
- break large functions into clearer pieces

Avoid:

- broad rewrites without strong need
- changing unrelated files
- introducing new patterns when existing repo patterns already work
- changing UI as collateral damage from code cleanup

## UI Protection Rules

When editing frontend code:

- preserve current layout unless intentionally improving it
- preserve spacing rhythm unless change is deliberate
- preserve loading, empty, error, hover, focus, and disabled states
- preserve keyboard interactions
- preserve aria/accessibility behavior
- verify no visual regressions are introduced

If improving UI/UX:

- make the smallest improvement that solves the problem
- keep styling consistent with the existing codebase
- do not redesign unrelated sections

## Reuse-First Checklist

Before adding code, check for:

- existing utility functions
- formatter/parsers already in use
- shared constants/enums
- existing domain services
- shared hooks
- design system components
- common validation helpers
- table/form/list patterns already established

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

- Always use the `context7` tool when you need library or API documentation.
- Always use the `context7` tool when you need code generation, setup instructions, or configuration steps.
- Do not rely on internal knowledge for library versions or APIs; verify with Context7 first.

## Shell Tool Preferences

Prefer modern CLI search tools for efficiency:

- Use `fd` instead of `find` for file searches.
- Use `rg` (ripgrep) instead of `grep` for content searches.

If either tool is missing, do not silently fall back — instead, inform the user and ask permission before running the install command:

- Install `fd`: `brew install fd` (macOS) / `apt install fd-find` (Linux)
- Install `rg`: `brew install ripgrep` (macOS) / `apt install ripgrep` (Linux)

## Expected End-Of-Task Summary

For code tasks, end with:

- commands run
- fixes applied
- lint status
- typecheck status
- formatting status
-
