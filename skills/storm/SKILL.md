---
name: storm
disable-model-invocation: true
argument-hint: "<problem statement> [--light] [--autonomous]"
description: Decide anything the heavy way — interview to one decision, pre-register a pick and its falsifier, research it through adversarial lenses, premortem and red-team the verdict, seed a wayfinder map. `--light` for judgment calls evidence cannot settle.
---

Goal: take any problem statement — technical or not, from a user who may know nothing
about the domain — reach shared understanding on **one decision** through an interview,
then autonomously build deep, sourced knowledge across research rounds and land on a
pick, recommending only when the evidence is strong enough, stating what is still unknown
first, and handing the remaining fog to `wayfinder`.

Method from Stanford OVAL's STORM (multi-perspective question asking, NAACL 2024) and
Co-STORM (a moderator mining uncited sources for new directions, EMNLP 2024). Bias
controls from open science (**pre-registration** and Popper's **falsifier**), Klein's
**premortem**, Wald's **survivorship** lesson (the graveyard), and the **council** pattern
(fresh voices that see only the question). Companion to `compass` (breadth across named
alternatives) and `oracle` (vertical unknown-unknowns); `storm` is the heavier sibling.

**The interview is the only gate** (plus one skippable checkpoint, Step 6). After the
user confirms shared understanding, every remaining step runs autonomously through to
the recommendation.

## Gears

- **Heavy** (default) — the full loop below: research, ledger, report file, wayfinder seed.
- **Light** (`--light`) — no research, no file. Steps 1–3, then Step 3L, then Step 10's
  verdict rules in chat. For judgment calls that evidence cannot settle: ship now or hold,
  cut scope or keep it, one repo or two. When the voices split on a *fact*, say so and
  offer heavy.

## Vocabulary

- **Decision** — the one question this run resolves. Say *decision*, not problem, topic, or
  ask.
- **Pick** — the recommended candidate. Say *pick*, not answer, solution, or choice.
- **Falsifier** — the observation that would kill the initial pick. Say *falsifier*, not
  risk, concern, or counter-argument.
- **Fog** — decisions this run surfaced but did not resolve; wayfinder's word, kept.

## Steps

### Step 1 — Interview to shared understanding

Check for Matt Pocock's `grilling` (`~/.claude/skills/grilling/` for Claude Code,
`~/.agents/skills/grilling/` for Codex, or the active profile's `skills/grilling/`).

**Found:** invoke `grilling` with the Skill tool — it drives the questioning round by
round and dispatches its own sub-agents for facts; seed it and wait.

**Missing:** run the same interview inline with the `AskUserQuestion` tool, keeping the
grilling contract: ask the whole frontier each round — every question whose
prerequisites are settled — with a recommended answer per question; look facts up
yourself instead of asking the user; recompute the frontier after each round of answers;
the interview ends when the frontier is empty.

Either way, seed the interview with the problem statement and direct it to surface: the
user's domain knowledge (assume none until shown otherwise), hard constraints (budget,
deadline, locale, stack), the goal behind the ask, preferences and dealbreakers, and
the report file destination (default `./storm-report-<topic-slug>.md`).

**One decision per storm.** A big problem is several decisions. When the interview
surfaces more than one, put each to the user by name and ask which one this run takes;
the rest are listed in chat as *separate storm candidates* and land in the report's
Out of scope. When the problem lives in a repository, the interview also records the
repo path — Step 5 measures there.

**Done when:** exactly one decision is named in one line, the extra decisions are listed,
and the user confirms shared understanding — the last interactive moment before the
checkpoint. Announce that storm now runs autonomously, then continue without stopping.

### Step 2 — Premise challenge

Before any research, dispatch one fresh sub-agent as the **Skeptic**. It receives only
the decision line and the constraints from Step 1 — none of the conversation. It answers,
under 200 words: which assumption, if false, dissolves the decision; the simplest
credible alternative framing; whether the question is the right one.

A reframe that survives your own reading goes back to the user as a single
`AskUserQuestion` (accept the reframe or keep the original); this is still the interview.
"Premise holds" is recorded verbatim.

**Done when:** the Skeptic's three answers are recorded and the decision line is final.

### Step 3 — Pre-register

Write, before any evidence arrives and verbatim into the report later: your **initial
pick**, the three strongest reasons for it, its biggest risk, and its **falsifier** — the
observation that would kill it. When a repo is in play, the falsifier is a measurement
(`bundle < 300 KB gzip`, `p95 < 800 ms`), not an opinion.

**Done when:** the four items are written down and the falsifier is checkable.

### Step 3L — Light gear only: council

Launch three fresh sub-agents in parallel — **Skeptic**, **Pragmatist** (shipping speed,
user impact, operational reality), **Critic** (edge cases, downside risk, failure modes).
Each receives only the decision line, the constraints, and the compact context the
decision needs, never the conversation. Each returns: position (1–2 sentences), three
reasons, biggest risk, one thing the other voices may miss. Under 300 words. Your
pre-registered pick is the fourth voice, the **Architect**.

Then go to Step 10 and apply its synthesis rules to the four positions; the verdict goes
to chat, ending with the wayfinder seed in the shape of Step 10.

**Done when:** four positions are visible before the verdict.

### Step 4 — Generate candidates

Dispatch one fresh sub-agent with the decision line and constraints only. It returns at
least five genuinely distinct candidates, always including **do nothing** and the
**inversion** (the opposite of the obvious move), each in one line with the axis it wins
on. Your initial pick is added to the set if missing; it earns no special place.

**Done when:** the candidate set has ≥5 entries including do-nothing and inversion.

### Step 5 — Pick 5 lenses for *this* decision

Restate the decision in one line. Two lenses are fixed:

- **Disconfirmation** — hunts evidence against the current leading candidate and for the
  falsifier.
- **Graveyard** — hunts failures: postmortems, rollbacks, abandoned attempts, base rates.
  Successes are the survivors; this lens reads the planes that did not come back.

Choose the other three for the decision at hand — a DB choice → practitioner,
scalability engineer, cost/ops; a photoshoot-company pick → past client, working
photographer, budget analyst. Fall back to practitioner, academic, economist only if the
decision resists specialisation.

**Done when:** 5 lenses stand, each with a one-line why tied to an interview constraint.

### Step 6 — Research round *(loop entry — round counter starts at 1 here)*

Research before asserting — retrieved facts only, gathered by **parallel sub-agents**,
one per lens (round 1) or per moderator question (later rounds), launched in a single
batch. Each sub-agent runs 2–3 scoped `WebSearch` queries — plus `Context7` MCP when
the decision concerns a library / framework / API — ranks sources by
[`references/source-priority.md`](references/source-priority.md) (read it first),
and returns: core position (2 sentences) · strongest evidence with cited source · the
one thing only this lens would tell you · every source it retrieved.

**Local evidence.** When the interview recorded a repo, each lens also measures there,
read-only: build reports, bundle analyzers, Lighthouse via the browser MCP, query plans,
log timings, test runs. A measurement enters the ledger as a source with the exact
command and the number it produced. Sub-agents measure; they never edit.

Merge the returns into the **source ledger**: every source retrieved this round, marked
*cited* or *uncited* once the round's outputs are written. The ledger is the moderator's
raw material (Step 9).

**Done when:** every lens or question has its four-part output, every claim cited,
every retrieved source in the ledger, and the falsifier is marked *hit*, *missed*, or
*untested*.

### Step 7 — Contradiction map

1. **Conflicts** — where ≥2 lenses clash, with the colliding claims.
2. **Evidence weight** — strongest and weakest lens, and why.
3. **Pivotal question** — the one that resolves the biggest conflict.
4. **Consensus** — what every lens agrees on; even opponents confirm it.
5. **Blind spot** — what no lens addressed. Hunt it with `oracle`'s descent move
   (`../oracle/SKILL.md` Step 3): dispatch one sub-agent to ask, for each gap, what
   concept it presupposes, what mechanism it hides, what failure mode it papers over —
   and recurse. Gaps found feed the moderator (Step 9).

**Checkpoint (round 1 only, skipped under `--autonomous`):** show the map and the
pivotal question, then ask one `AskUserQuestion`: *is any constraint from the interview
wrong?* Corrections update the constraints; preferences among candidates are not taken
here.

**Done when:** all five parts written; from round 2 on, each prior conflict marked
resolved or still open.

### Step 8 — Synthesis

1. **5 key findings**, ranked by reliability; per finding, which lenses support and
   which challenge it.
2. **Hidden connection** — one non-obvious link visible only across lenses.
3. **Candidates** — start from the Step 4 set; kill or add only with a cited finding.
   Build the surface with `compass`'s frame (`../compass/SKILL.md` Steps 2, 4–5): name
   the axes that dominate this decision and give each surviving candidate why / why-not /
   when-to-pick — each why naming an axis, backed by the cited findings. The verdict
   stays with Step 10; synthesis maps the surface only.

**Done when:** every finding traces to cited sources, every candidate carries all three
facets tied to a named axis, and every kill names its finding.

### Step 9 — Moderator *(loop or exit — Co-STORM)*

Mine two seams for new questions: **(a)** uncited ledger entries — retrieved
information no output used; **(b)** open items from Step 7 — unresolved conflicts, the
pivotal question, the blind spot, an untested falsifier. Rank candidate questions by
relevance to the decision and dissimilarity from questions already asked.

A question is **material** if its answer could change a candidate's ranking, move a
finding's reliability, or test the falsifier. Loop rule: after round 1, always carry the
top questions into Step 6 — two rounds minimum. After round 2, loop a third time only if
material questions remain. Three rounds is the cap; then → Step 10.

**Done when:** the loop decision is stated with the question list (or "none material")
and the round count.

### Step 10 — Red team, peer review, confidence-gated recommendation

1. **Draft verdict** — the leading candidate and why, one paragraph.
2. **Premortem** — it is one year on and the pick failed. Write the three most likely
   reasons, each tied to a finding or a gap.
3. **Critic** — dispatch one fresh sub-agent with only the draft verdict, the candidate
   surface, and the five findings. It answers: where the conclusion fails, which material
   failure mode is missing, whether the strongest opposing view was suppressed, and
   whether it would sign off. Quote it verbatim; do not rewrite it in your voice.
4. **Confidence scores** — each key finding 1–10 with reasoning.
5. **Weakest link** — the least-confident claim + what would verify it.
6. **Bias check** — which lens over-dominated the synthesis, and **evidence moved me:
   yes / no** — did the pick move from the pre-registered one, and on which finding. A
   pick that survived a *hit* falsifier is not a pick; demote it.
7. **Missing lens** — would a 6th change the conclusion.
8. **Synthesis rules** — the strongest dissent appears in the verdict even when
   rejected; a dismissed voice gets its reason; two lenses or voices aligned against the
   initial pick is treated as a real signal, never a coincidence.
9. **Recommendation rule** — state remaining unknowns first, each with `oracle`'s three
   teach lines (`../oracle/SKILL.md` Step 5): what it is / why it matters here / what
   breaks if ignored. Then, only if confidence suffices, give the pick with why / why-not
   and the "pick X instead if …" condition. If uncertainty is too high, **withhold the
   pick** and list exactly what info would unblock the decision.
10. **Recommended path** — directly below the verdict, a ~150-word first-person
    narrative arguing the pick like an advisor who must sign off, not a survey: what
    I'd do and in what order, which candidates I rejected and on which axis, which are
    conditional and on what. When rule 9 withholds the pick, the advisor argues the
    neutrality instead. Tag each candidate heading with the advisor's call: **picked**
    (+ role, e.g. backbone / add-on), **rejected: <one-line reason>**, or
    **conditional: <condition>**.
11. **Wayfinder seed** — the last body section, in the shape of a wayfinder map body so
    `/wayfinder <report path>` charts from it with a short interview:

    ```markdown
    ## Wayfinder seed

    ### Destination
    <the pick, restated as the end state this effort reaches>

    ### Notes
    <constraints from the interview; skills every session should consult>

    ### Decisions so far
    - <the pick>: <one-line gist> — <finding>
    - <each settled finding that closes a question>

    ### Not yet specified
    - <each remaining unknown from rule 9, one line, typed research / prototype / grilling / task>

    ### Out of scope
    - <each rejected candidate>: <reason>
    - <each separate-storm candidate from Step 1>
    ```

Write the report to the Step-1 path in two parts. **Body — a 5-minute read, ~1250
words max**, in order: unknowns first (with teach lines), verdict, recommended path,
premortem, confidence table, the 5 key findings, candidates (tagged) with why / why-not /
when-to-pick, wayfinder seed. **Appendix — below a `---` divider, skippable, no length
cap:** the pre-registration verbatim, the Skeptic and Critic outputs verbatim, per-round
research record, contradiction-map history, full source ledger, peer-review detail —
every claim cited.

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
  Measurements cite their ledger entry, which holds the command. Ledger entries
  themselves are markdown links.

**Done when:** the report file exists at the agreed path, its body reads in ≤5 minutes,
the bold lead-ins alone summarize the report (skim test), the Critic is quoted, the
falsifier's fate is stated, and chat shows the unknowns-first verdict + recommended path
+ `next: /wayfinder <report path>`.

## Output shape

- **Chat** — one progress line per step per round while autonomous; at the end,
  unknowns first, then the verdict + recommended path (or the withheld-pick unblock
  list), then the next-step line. Light gear: the four positions, then the verdict and
  seed, no file.
- **Report file** (heavy) — body and appendix as Step 10 orders them, at the
  interview-agreed path.

## Rejected framings

- *Planner.* Storm decides; `wayfinder` → `to-spec` → `to-tickets` → `implement` plan
  and build. Storm never writes a task list.
- *Several decisions per run.* Grilling is human-in-the-loop, so a sub-agent cannot run
  its own storm; running several in one thread muddles the pick and burns the smart zone.
- *Storm invokes wayfinder.* A heavy run spends most of the window; charting the map in
  the same context runs degraded. The seed is the handoff.
- *Candidate preference at the checkpoint.* Only constraints are corrected there; a
  thumb on the scale mid-run is the confirmation bias the loop exists to remove.
