---
name: storm
description: Decide an implementation by researching it from 5 adaptive expert perspectives, mapping where they contradict, synthesising sourced findings, then self peer-reviewing into a confidence-gated recommendation. Real WebSearch + Context7 sourcing, cited per claim. Runs as four interactive gated phases (scan → contradiction map → synthesis → peer review) and renders a visual MDX briefing. Use on "storm" or for deep research before an implementation / tooling / architecture decision where you want unknown-unknowns surfaced before picking.
---

Goal: build deep, sourced knowledge on a topic, surface the unknown-unknowns, then decide which implementation to go with — recommending only when the evidence is strong enough, and stating what is still unknown before the recommendation.

STORM = Synthesis of Topic Outlines through Retrieval and Multi-perspective question asking (Stanford OVAL, NAACL 2024). Companion to `compass` (breadth across named alternatives) and `oracle` (vertical unknown-unknowns). `storm` is the heavier sibling — it runs the full multi-perspective → contradiction → synthesis → peer-review loop and lands on a confidence-gated pick.

Run the four phases as **interactive gates**: after each phase, print the result in chat and stop for the user to review before continuing.

## Steps

### Phase 1 — Multi-perspective scan (adaptive personas)

1. **Restate.** One line: the topic + the decision to be made.
2. **Pick 5 expert lenses for *this* topic.** Choose the perspectives that actually matter here — e.g. a DB choice → practitioner, scalability engineer, cost/ops, security, maintainer. Fall back to the article's generic 5 (practitioner, academic, skeptic, economist, historian) only if the topic is too broad to specialise. State the chosen 5 + a one-line why for each.
3. **Research before asserting — do not simulate knowledge.** Per lens: `WebSearch` for the landscape and what practitioners actually ship; `Context7` MCP for library / framework / API docs. Rank sources by `../../.shared-agents/common/source-priority.md` (read it before searching) and **cite the source per claim**.
4. **Per lens, output:** core position (2 sentences) · strongest evidence (with cited source) · the one thing only this lens would tell you.
5. **Gate** → wait for the user.

### Phase 2 — Contradiction map

1. **Conflicts.** Where do ≥2 lenses directly clash? List each with the specific claims that collide.
2. **Evidence weight.** Which lens has the strongest evidence, which the weakest, and why.
3. **The pivotal question** that, if answered, resolves the biggest conflict.
4. **Consensus.** What every lens agrees on — likely true, since even opponents confirm it.
5. **Blind spot.** What no lens addressed — the unknown-unknown, often the most valuable finding.
6. **Gate** → wait for the user.

### Phase 3 — Synthesis briefing

1. **One-paragraph summary** for someone with 60 seconds who needs nuance, not the headline.
2. **5 key findings**, ranked by reliability; per finding note which lenses support and which challenge it.
3. **Hidden connection** — one non-obvious link visible only across all 5 lenses.
4. **Candidate implementations** — the decision surface: per candidate give why / why-not / when-to-pick, backed by the sourced findings above (this is the `compass`-style comparison, now evidence-led).
5. **Gate** → wait for the user.

### Phase 4 — Peer review + confidence-gated recommendation

1. **Confidence scores.** Rate each key finding 1–10 for reliability, with reasoning.
2. **Weakest link.** The least-confident claim + the specific info that would verify it.
3. **Bias check.** Which lens over-dominated the synthesis.
4. **Missing perspective.** Is there a 6th lens that would change the conclusions.
5. **Recommendation rule.** State remaining unknowns / unverified items **first**. Then — only if confidence is sufficient — give the recommended implementation with why / why-not, plus the "pick X instead if …" condition. **If uncertainty is too high, withhold the pick** and list exactly what info would unblock the decision.
6. **Gate** → offer to render the visual MDX briefing.

## Visual output

Reuse the `visual-plan` skill's machinery — do not re-document its blocks here.

1. Read `visual-plan`'s reference files (`references/document-quality.md`, `references/wireframe.md`, `references/canvas.md`) and run `npx @agent-native/core@latest plan blocks` for the authoritative block catalog before authoring.
2. Emit a **plan-style** MDX doc to `plans/<slug>/plan.mdx` (frontmatter: title, brief, `kind: plan`, created). Suggested mapping:
   - 5 perspectives → `TabsBlock`, one tab per lens, each `RichText` with cited evidence.
   - Contradiction map → `Diagram` (lenses as nodes, clashes as edges) + `Callout`s for consensus ("likely true") and blind spot ("unknown-unknown").
   - Synthesis → `RichText` summary + ranked findings; candidates as `Columns` or a table (why / why-not / when-to-pick).
   - Peer review → confidence-score table; `Callout` for weakest link + bias; unblock-questions in a `QuestionForm`.
   - Recommendation → `Callout` (decision tone), with the gaps stated above it.
3. Validate then serve: `plan local check --dir plans/<slug>`, then `plan local serve --dir plans/<slug> --kind plan --open`.
4. **Fallback:** if `@agent-native/core` is not installed, render one self-contained HTML artifact with the same sections so the skill works standalone.

## Output shape

- **Per phase, in chat behind a gate** — Phase 1 lenses + cited evidence · Phase 2 contradiction map · Phase 3 synthesis + candidates · Phase 4 peer-review scores + recommendation.
- **Then a visual MDX briefing** (or HTML fallback) carrying the perspectives, contradiction map, sourced synthesis, confidence scores, and the confidence-gated recommendation with its stated gaps.
