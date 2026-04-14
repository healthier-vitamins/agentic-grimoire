---
name: coexistence
description: Use this skill when a task should begin with repository inspection and produce a concrete implementation plan before code changes.
---

# Coexistence

Use this skill when a task should begin with repository inspection and produce a concrete implementation plan before code changes.

## Objective

Act as a Staff Engineer inside this repository.

Given the technical task above, inspect the codebase first and produce a detailed implementation plan before writing code.

## Core requirements

1. Cover the original task fully.
2. Break it into smaller tasks if it is large.
3. For each task, inspect the codebase and explain how it should fit the current architecture.
4. Reuse existing patterns, utilities, modules, and conventions wherever possible.
5. Brainstorm solution options grounded in the repo, and only introduce new libraries if necessary.
6. Use Context7 or equivalent up-to-date documentation to validate any library/framework usage.
7. Avoid breaking existing functionality; call out regressions and compatibility risks.
8. Keep the approach DRY and logically abstracted.
9. Align with the repository’s structure, naming, formatting, and architecture.

## Output requirement

Produce a structured planning report containing:

- task restatement
- codebase findings
- constraints and assumptions
- granular task breakdown
- solution options and recommendation
- integration plan
- regression analysis
- dependency and library notes
- testing strategy
- implementation order
- pitfalls and gotchas
- foundational logic
- advanced considerations
- open questions
- concise recommendation summary

## Operating rules

- Inspect the repository before proposing implementation.
- Use actual repo file paths, modules, symbols, and patterns where possible.
- Do not make unverified claims.
- Prefer incremental, low-risk changes.
- Extend existing architecture before inventing new abstractions.
- Only suggest new libraries if the current stack cannot solve the problem cleanly.
- If suggesting a new dependency, explain why existing tools are insufficient.
- Explicitly call out areas where existing functionality could break.
- Be concrete and specific, not generic.

## Suggested workflow

1. Inspect repository structure and entrypoints.
2. Find the relevant modules, services, components, schemas, routes, tests, and configs.
3. Identify similar existing implementations and conventions.
4. Determine constraints and likely regression points.
5. Evaluate implementation options grounded in the codebase.
6. Validate any library/framework usage with Context7 or equivalent current documentation.
7. Produce the planning report.

## Preferred structure of the planning report

# Task Planning Report

## 1. Original Task

Restate the task clearly, including explicit requirements and any reasonable inferred requirements.

## 2. Codebase Findings

Summarize the relevant architecture, important files, existing patterns, and similar implementations already present in the repo.

## 3. Constraints and Assumptions

List technical, architectural, operational, and business constraints. Mark uncertain assumptions clearly.

## 4. Task Breakdown

Break the work into granular tasks. For each task, include:

- purpose
- relevant existing files/patterns
- what should be reused
- what needs to change
- risk level
- dependencies

## 5. Solution Options Considered

List meaningful implementation options, with pros, cons, architecture fit, and final recommendation.

## 6. Integration Plan

Explain how the solution fits into the current system:

- touchpoints
- execution flow
- data flow
- state flow
- APIs/contracts
- schema impact
- infra/deployment impact if any

Use simple diagrams if helpful.

## 7. Regression and Compatibility Analysis

Identify likely breakpoints, edge cases, migration concerns, rollback concerns, and blast-radius reduction steps.

## 8. Dependencies / Libraries / External References

List existing dependencies involved. If new ones are proposed, justify them carefully and verify current usage patterns with Context7 or equivalent.

## 9. Testing Strategy

Cover unit, integration, e2e, manual validation, regression cases, and observability/logging where relevant.

## 10. Implementation Order

Provide the safest order of execution, including prerequisites, risky steps, checkpoints, and parallelizable work.

## 11. Pitfalls and Gotchas

Give this section real attention. Identify codebase-specific footguns, not generic warnings. Focus on subtle failure modes, hidden contracts, duplication traps, architecture mismatches, outdated patterns, and regression-prone changes.

## 12. Foundational Logic

Give this section real attention. Explain why the recommended approach works in this repository, what tradeoffs it makes, and what engineering principles are driving the decision. The plan should not feel like a black box.

## 14. Open Questions

List only genuine unresolved questions that materially affect implementation.

## 15. Recommendation Summary

End with:

- recommended approach
- why it best fits the repo
- highest-risk area
- first implementation step

## Quality bar

The final plan should read like it was written by a senior engineer who understands the current system, respects existing constraints, avoids unnecessary rewrites, and recommends practical, maintainable changes.

Do not over-index on novelty. Prefer the most maintainable solution that fits the existing codebase well.

Give extra care to:

- hidden regressions
- codebase-specific pitfalls
- the reasoning behind the recommendation

But keep the overall report balanced and complete.
