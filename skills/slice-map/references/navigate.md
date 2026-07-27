# Navigate a slice map

## 1. Reconcile progress

Read the approved map and evidence of work completed since its latest revision.
Ask the user only for status facts that the repository or tracker cannot show.
Update statuses and append one dated revision entry naming the evidence used.

When the evidence changes a future boundary, prerequisite, or gate, enter
**Revise** before recommending work.

**Done when:** every status change has evidence and the revision history records
the reconciliation.

## 2. Recompute the route

Regenerate the dependency graph, critical path, and full frontier from the
canonical slice index. Apply the computation rules in `../SKILL.md`.

**Done when:** every derived view agrees with the slice index and every frontier
slice has status `Open` with all blockers `Done`.

## 3. Recommend one next slice

Choose exactly one takeable slice with `../SKILL.md`'s recommendation rule.
Explain the downstream gate it clears and the independently verifiable outcome
it delivers. For a leaf slice, state that it clears no gate and give the useful
outcome or risk reason instead.

**Done when:** the map and chat name exactly one takeable next slice and give its
gate-clearing, useful-outcome, or risk reason.
