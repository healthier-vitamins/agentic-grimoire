# DRY And Simple Code

Use this skill when writing or revising implementation logic.

## Objective

Write the simplest maintainable solution with minimal duplication.

## Rules

- Reuse existing code first.
- Prefer explicit code over clever abstractions.
- Extract helpers only when reuse is real and naming is clear.
- Keep functions focused.
- Prefer readable branching over compressed one-liners.
- Avoid introducing generic utilities too early.

## Heuristics

- If abstraction makes the code harder to read, do not extract yet.
- If duplication appears in multiple stable places, extract it.
- If a helper name is unclear, keep the logic inline until the abstraction becomes obvious.
