# Refactor Safely

Use this skill when changing existing code.

## Objective

Improve code without breaking behavior.

## Rules

- Prefer the smallest safe refactor.
- Preserve public interfaces unless the task explicitly requires change.
- Do not mix unrelated cleanup into the same diff.
- Keep data flow explicit.
- Keep side effects where callers expect them.
- Preserve loading, empty, and error states.

## Refactor checklist

1. Identify current behavior first.
2. Identify what is duplicated, confusing, or risky.
3. Refactor only the touched area unless expansion is necessary.
4. Preserve behavior with tests or strong local reasoning.
5. Re-run validation after the change.

## Good candidates

- duplicated conditionals
- fragile null handling
- deeply nested branches
- repeated data mapping
- repeated UI state rendering
- confusing names
- overly long functions

## Avoid

- large rewrites
- hidden behavior changes
- silent API contract changes
- opportunistic redesign
