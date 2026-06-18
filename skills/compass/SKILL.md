---
name: compass
description: Orient across the full option space for a proposed solution — surface ≥3 genuinely distinct alternatives, weigh each why / why-not / when-to-pick, and close with an opinionated verdict. WebSearch required. Use on "compass" / "alternatives" / "what else could I use" or when comparing solutions horizontally.
---

Goal: given a chosen solution, map the solutions not taken — explore the option space horizontally and recommend a pick.

Companion to `oracle` (which explores one stack vertically — depth, unknown-unknowns). `compass` explores breadth across competing approaches.

## Steps

1. **Restate the proposed solution + intent.** One line naming the chosen approach and the problem it solves. This is the baseline everything else is compared against.

2. **Frame the axes that matter.** Name the dimensions alternatives differ on for *this* problem — e.g. latency, throughput, ops cost, consistency, lock-in, team familiarity, scaling ceiling. The right alternatives are decided by these axes, not by popularity.

3. **Research — WebSearch is mandatory.** Find what practitioners actually ship, not what blogs recommend in the abstract.

   **Source priority (highest first):**
   1. Big-tech engineering blogs & published design specs — Google, Meta, Amazon, Netflix, Microsoft, Apple, plus Uber, Grab, Airbnb, Stripe, etc.
   2. Official documentation for the library / framework / API (`Context7` MCP, or the canonical docs site).
   3. Reputable engineering newsletters, public RFCs, and architecture decision records.

   Avoid SEO content farms, unattributed reposts, and AI-generated listicles. Cite the source per claim.

4. **Surface ≥3 alternatives** (more if the space allows). The proposed solution is one point in the space; the others are *genuinely distinct* approaches — not config variations of the same thing.

5. **Per alternative, give four facets:**
   - **What it is** — one line.
   - **Why** — where it wins on the axes above.
   - **Why not** — where it loses.
   - **When to pick it** — the specific constraint that makes it the right call.

6. **Verdict.** Recommend one for the user's stated constraints, with rationale. Then name the constraint under which a different pick wins ("pick X instead if …").

## Output shape

- **Proposed solution + intent** — one line.
- **Axes that matter** — short bulleted list.
- **Alternatives** — ≥3, each with what / why / why-not / when-to-pick (+ a cited source).
- **Verdict** — recommended pick + the "pick X instead if …" condition.
