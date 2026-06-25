---
name: lathe
description: Interrogate a task, decide whether it needs a one-shot prompt, a workflow, or an autonomous loop (/goal), then forge the ready-to-run artifact. Use on "lathe", "forge a prompt", "should this be a loop/goal", or when starting a task and unsure whether to hand-prompt it or let an agent loop on it.
---

Goal: turn a rough task into the right-shaped artifact. Decide the tier on Anthropic's complexity ladder — single prompt → workflow → autonomous loop — then forge it. Companion to `compass` (breadth of alternatives) and `oracle` (depth, unknown-unknowns).

Default to the **simplest** tier that works. Climb only when it demonstrably earns the extra cost. The load-bearing question is always: **is there a machine-checkable oracle?** No oracle ⇒ no loop.

## Step 1 — Interview (grill-me style)

Ask **≤6** questions, **one at a time**, ordered by criticality. Give your **recommended answer** with each. If a question is answerable by reading the codebase, explore instead of asking. Combine closely related sub-questions into one.

Extract these decision signals:

1. **Oracle** — is there a machine-checkable pass/fail? (tests / typecheck / lint / build / a measurable threshold) — *load-bearing*
2. **Done** — is "done" objective, or a matter of taste/judgment?
3. **Spec** — bounded and clear, or exploratory? Predictable step count, or unknown?
4. **Cadence** — runs once, or repeats (≈weekly+)?
5. **Autonomy** — can the agent do it end-to-end, including any actions/connectors it needs?
6. **Budget** — tolerable iteration/token cap; rough cost-per-accepted-change?

## Step 2 — Decision gate

Route with these rules (first match wins):

- **No oracle**, OR **taste-based** done, OR **exploratory/ambiguous** spec → **one-shot prompt** (+ human review).
- Oracle exists, path is **predictable** and multi-step, bounded → **workflow** (prompt-chaining / routing / evaluator-optimizer).
- Oracle exists **and** step count is **unpredictable**, OR it **repeats**, OR needs **end-to-end autonomy** → **autonomous loop (`/goal`)**.

Tie-breakers: a single objective question with a clear pass/fail and few turns → still a prompt. Loop only when iteration against the oracle adds real value over one pass.

## Step 3 — Forge

Fill the matching template in [references/templates.md](references/templates.md). Then output, in order:

1. **Tier** chosen + a one-line **why** ("loop: tests give a hard oracle and step count is unknown" / "one-shot: done is taste-based, no oracle").
2. The **artifact** in a single copy-paste block.
3. For the loop tier only: the **runnable command** form (`/goal …`) plus the agent-notes block from the template.

## Pitfalls (check before shipping a loop)

- **Premature-done** (Ralph Wiggum) — agent declares victory early. Make the stop condition verifiable, ban placeholder/stub "done".
- **Self-grading** — the maker is a soft grader of itself. Use a separate checker, ideally a different model family.
- **Scope/goal drift** — an unbounded goal never exits. Always pair completion condition **with** an iteration/budget cap.
- **Cost** — context re-bills ~O(n²) per iteration. Lean on prompt caching; track cost-per-accepted-change, not tokens. Below ~50% accept rate the loop costs more than it saves.
- **No oracle ⇒ don't loop.** Drop to one-shot + human review.

Full checklist and sourcing: [references/templates.md](references/templates.md).
