# Preserve UI Behavior

Use this skill for frontend or component changes.

## Objective

Allow improvements without causing visual or interaction regressions.

## Rules

- Preserve existing layout intent.
- Preserve accessibility and keyboard interaction.
- Preserve focus behavior.
- Preserve responsive behavior.
- Preserve empty, loading, success, and error states.
- Avoid changing spacing, copy, or alignment unless part of the task.

## Safe change examples

- fixing broken alignment
- improving accessibility labels
- simplifying duplicated render branches
- reducing rerenders without changing UI behavior
- improving disabled/loading state consistency

## Before finishing

- compare old and new rendered states mentally or with tests
- verify no unrelated visual change was introduced
