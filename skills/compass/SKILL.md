---
name: compass
disable-model-invocation: true
description: Traverse the option space horizontally — surface the alternatives to a chosen solution and recommend a pick.
---

Goal: given a chosen solution, map the solutions not taken — explore the option space horizontally and recommend a pick.

Companion to `oracle` (which explores one stack vertically — depth, unknown-unknowns). `compass` explores breadth across competing approaches.

**When not to use:** for open exploration — "how should I think about X", general research — the bare harness is the better default; it plans its own approach and reads more cohesively than a fixed procedure. Reach for `compass` when a choice is already made or leaning, and you want it attacked and a verdict issued.

## Steps

0. **Misfit check.** `compass` misfits when no solution has been proposed — there is no baseline to compare against, so the skill would have to invent one, which is where it drifts generic. That is the whole test.

   On misfit, name the absent trigger in one line, then answer directly and skip the rest:

   > Skipping `compass`: no solution proposed — no baseline to compare alternatives against. Answering directly.

1. **Restate the proposed solution + intent.** One line naming the chosen approach and the problem it solves. This is the baseline everything else is compared against.

2. **Frame the axes that matter.** Name the dimensions alternatives differ on for *this* problem — e.g. latency, throughput, ops cost, consistency, lock-in, team familiarity, scaling ceiling. These axes pick the field: the alternatives worth surfacing are the ones that win or lose meaningfully on them.

   Aim: the axes dominating *this* decision are named, and every later alternative can be placed on them.

3. **Research — WebSearch is mandatory.** Rank sources by `../../.shared-agents/common/source-priority.md` — read it before searching, and cite the source per claim.

   Aim: every alternative in step 5 carries a cited source.

4. **Surface ≥3 alternatives** (more if the space allows). The proposed solution is one point in the space; the others are *genuinely distinct* approaches — different in kind. A re-tuning of the proposed solution is that same point again, not an alternative.

   This quota is the point of the skill — the alternative the user would never have thought to ask about is the payload. Surface it even when it loses.

   Aim: ≥3 genuinely distinct approaches stand, none a config variation of another.

5. **Per alternative, give four facets:**
   - **What it is** — one line.
   - **Why** — where it wins on the axes above.
   - **Why not** — where it loses.
   - **When to pick it** — the specific constraint that makes it the right call.

   A clear loser may be dispatched in a line or two so the space goes to the live contenders — a length allowance only: it is still named, still placed on the axes, still in the output.

   Aim: every alternative is placed, each *why* / *why not* naming an axis from step 2.

6. **Verdict.** Recommend one for the user's stated constraints, with rationale. Then name the constraint under which a different pick wins ("pick X instead if …").

   Aim: one pick named for the stated constraints, plus the "pick X instead if …" condition.

## Output shape

A default, not a template — reshape when the material calls for it.

- **Proposed solution + intent** — one line.
- **Axes that matter** — short bulleted list.
- **Alternatives** — ≥3, each with what / why / why-not / when-to-pick (+ a cited source).
- **Verdict** — recommended pick + the "pick X instead if …" condition.
