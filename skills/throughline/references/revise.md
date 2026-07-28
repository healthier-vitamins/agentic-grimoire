# Revise a throughline

## 1. Bound the change

Record the new fact and identify every unfinished slice, coverage row, and edge it affects.
Preserve completed slices as immutable history.

**Done when:** every affected unfinished item is named and every completed item is either
unaffected or retained unchanged.

## 2. Re-slice unfinished work

Re-slice only unfinished behaviours. Rerun the coverage audit, prerequisite test, edge test,
cycle check, and deterministic critical-path computation from `../SKILL.md`.

**Done when:** every affected source item is accounted for exactly once, every prerequisite
and gate passes its test, the graph is acyclic, and every derived view agrees with the slice
index.

## 3. Approve the revision

Set the status to `Draft`, regenerate every derived section, and append one dated revision
entry naming the fact and its effects. Show only the changed portion and its downstream
consequences to the user. Return the throughline to `Approved` on confirmation.

**Done when:** the canonical throughline records an approved revision and completed history
remains immutable.

## 4. Resume navigation

Read `navigate.md` completely and run it against the approved revision.

**Done when:** the revised throughline and chat name exactly one takeable next slice.
