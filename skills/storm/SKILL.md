---
name: storm
disable-model-invocation: true
description: Decide anything the heavy way — a batch-grill-me interview to shared understanding, then autonomous rounds of multi-lens research, contradiction-mapped, moderator-driven, and peer-reviewed into a confidence-gated pick.
---

Goal: take any problem statement — technical or not, from a user who may know nothing
about the domain — reach shared understanding through an interview, then autonomously
build deep, sourced knowledge across research rounds and land on a pick, recommending
only when the evidence is strong enough and stating what is still unknown first.

Method from Stanford OVAL's STORM (multi-perspective question asking, NAACL 2024) and
Co-STORM (a moderator mining uncited sources for new directions, EMNLP 2024). Companion
to `compass` (breadth across named alternatives) and `oracle` (vertical unknown-unknowns);
`storm` is the heavier sibling — interview, then the full loop, then a gated pick.

**The interview is the only gate.** After the user confirms shared understanding
(Step 1), every remaining step runs autonomously through to the recommendation.

## Steps

### Step 1 — Interview to shared understanding

Check for `batch-grill-me` (`~/.claude/skills/batch-grill-me/` for Claude Code,
`~/.agents/skills/batch-grill-me/` for Codex, or the active profile's
`skills/batch-grill-me/`).

**Found:** hand the interview to `batch-grill-me` — it drives the questioning round by
round and dispatches its own sub-agents for facts; seed it and wait.

**Missing:** run the same interview inline with the `AskUserQuestion` tool, keeping the
batch-grill-me contract: ask the whole frontier each round — every question whose
prerequisites are settled — with a recommended answer per question; look facts up
yourself instead of asking the user; recompute the frontier after each round of answers;
the interview ends when the frontier is empty.

Either way, seed the interview with the problem statement and direct it to surface: the
user's domain knowledge (assume none until shown otherwise), hard constraints (budget,
deadline, locale, stack), the goal behind the ask, preferences and dealbreakers, and
the report file destination (default `./storm-report-<topic-slug>.md`).

**Done when:** the user confirms shared understanding — the last interactive moment.
Announce that storm now runs autonomously to the recommendation, then continue without
stopping.

### Step 2 — Pick 5 expert lenses for *this* topic

Restate topic + decision in one line. Choose the 5 lenses that matter *here* — a DB
choice → practitioner, scalability engineer, cost/ops, security, maintainer; a
photoshoot-company pick → past client, working photographer, budget analyst, logistics
planner, reputation checker. Fall back to the generic 5 (practitioner, academic,
skeptic, economist, historian) only if the topic resists specialisation.

**Done when:** 5 lenses stand, each with a one-line why tied to an interview constraint.

### Step 3 — Research round *(loop entry — round counter starts at 1 here)*

Research before asserting — retrieved facts only, gathered by **parallel sub-agents**,
one per lens (round 1) or per moderator question (later rounds), launched in a single
batch. Each sub-agent runs 2–3 scoped `WebSearch` queries — plus `Context7` MCP when
the topic is a library / framework / API — ranks sources by
[`references/source-priority.md`](references/source-priority.md) (read it first),
and returns: core position (2 sentences) · strongest evidence with cited source · the
one thing only this lens would tell you · every source it retrieved.

Merge the returns into the **source ledger**: every source retrieved this round, marked
*cited* or *uncited* once the round's outputs are written. The ledger is the moderator's
raw material (Step 6).

**Done when:** every lens or question has its three-part output, every claim cited,
every retrieved source in the ledger.

### Step 4 — Contradiction map

1. **Conflicts** — where ≥2 lenses clash, with the colliding claims.
2. **Evidence weight** — strongest and weakest lens, and why.
3. **Pivotal question** — the one that resolves the biggest conflict.
4. **Consensus** — what every lens agrees on; even opponents confirm it.
5. **Blind spot** — what no lens addressed. Hunt it with `oracle`'s descent move
   (`../oracle/SKILL.md` Step 3): dispatch one sub-agent to ask, for each gap, what
   concept it presupposes, what mechanism it hides, what failure mode it papers over —
   and recurse. Gaps found feed the moderator (Step 6).

**Done when:** all five parts written; from round 2 on, each prior conflict marked
resolved or still open.

### Step 5 — Synthesis

1. **5 key findings**, ranked by reliability; per finding, which lenses support and
   which challenge it.
2. **Hidden connection** — one non-obvious link visible only across lenses.
3. **Candidates** — the decision surface, built with `compass`'s frame
   (`../compass/SKILL.md` Steps 2, 4–5): name the axes that dominate this decision,
   surface ≥3 genuinely distinct candidates, and give each why / why-not /
   when-to-pick — each why naming an axis, backed by the cited findings. The verdict
   stays with Step 7; synthesis maps the surface only.

**Done when:** every finding traces to cited sources and every candidate carries all
three facets, each tied to a named axis.

### Step 6 — Moderator *(loop or exit — Co-STORM)*

Mine two seams for new questions: **(a)** uncited ledger entries — retrieved
information no output used; **(b)** open items from Step 4 — unresolved conflicts, the
pivotal question, the blind spot. Rank candidate questions by relevance to the decision
and dissimilarity from questions already asked.

A question is **material** if its answer could change a candidate's ranking or move a
finding's reliability. Loop rule: after round 1, always carry the top questions into
Step 3 — two rounds minimum. After round 2, loop a third time only if material
questions remain. Three rounds is the cap; then → Step 7.

**Done when:** the loop decision is stated with the question list (or "none material")
and the round count.

### Step 7 — Peer review + confidence-gated recommendation

1. **Confidence scores** — each key finding 1–10 with reasoning.
2. **Weakest link** — the least-confident claim + what would verify it.
3. **Bias check** — which lens over-dominated the synthesis.
4. **Missing lens** — would a 6th change the conclusion.
5. **Recommendation rule** — state remaining unknowns first. Then, only if confidence
   suffices, give the pick with why / why-not and the "pick X instead if …" condition.
   If uncertainty is too high, **withhold the pick** and list exactly what info would
   unblock the decision.
6. **Recommended path** — directly below the verdict, a ~150-word first-person
   narrative arguing the pick like an advisor who must sign off, not a survey: what
   I'd do and in what order, which candidates I rejected and on which axis, which are
   conditional and on what. When rule 5 withholds the pick, the advisor argues the
   neutrality instead — the evidence genuinely splits, and here is what would unblock
   it. Tag each candidate heading with the advisor's call: **picked** (+ role, e.g.
   backbone / add-on), **rejected: <one-line reason>**, or **conditional: <condition>**.

Write the report to the Step-1 path in two parts. **Body — a 5-minute read, ~1250
words max**, in order: unknowns first, verdict, recommended path, confidence table,
the 5 key findings, candidates (tagged) with why / why-not / when-to-pick.
**Appendix — below a `---` divider, skippable, no length cap:** per-round research
record, contradiction-map history, full source ledger, peer-review detail — every
claim cited.

Formatting contract — the body is written to be skimmed:

- Each key finding: **bold one-line claim**, then 2–4 labeled sub-bullets
  (evidence · challenged by · so what), no bullet over 2 sentences.
- Nuance that doesn't fit a bullet sinks to the appendix — trimmed from the body,
  never deleted.
- Appendix lens entries use labeled bullets — Position / Evidence / Unique insight /
  Sources — not run-on paragraphs.
- Citations are compact inline links at the point of the claim —
  `([source label](url))` — at most 2 per bullet. Link only URLs actually retrieved
  (they are in the ledger); a claim without a captured URL cites its ledger entry.
  Ledger entries themselves are markdown links.

**Done when:** the report file exists at the agreed path, its body reads in ≤5 minutes,
the bold lead-ins alone summarize the report (skim test), and chat shows the
unknowns-first verdict + recommended path.

## Output shape

- **Chat** — one progress line per step per round while autonomous; at the end,
  unknowns first, then the verdict + recommended path (or the withheld-pick unblock
  list).
- **Report file** — 5-minute skimmable body (unknowns → verdict → recommended path →
  confidence table → findings → candidates, tagged) + cited appendix, at the
  interview-agreed path.
