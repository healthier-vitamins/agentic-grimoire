# The style

Distilled from Matt Pocock's skills (aihero.dev). The standard `skillsmith` forges against — every question in the interview, every derivation, every audit row traces to a section here.

## 1. Predictability

A skill exists to wrangle determinism out of a stochastic system. The root virtue is the agent taking the same **process** every run — not producing the same output. Every principle below serves this.

## 2. Two loads

Every skill spends one of two currencies, and invocation is the fork:

- **Model-invoked** — the description sits in the context window every turn (**context load**), but the agent and other skills can reach it autonomously.
- **User-invoked** (`disable-model-invocation: true`) — zero context load, but the user's memory is now the index (**cognitive load**).

Pick model-invocation only when the agent must fire it on its own or another skill must reach it. When user-invoked skills multiply past memory, a **router skill** — one skill that names the others and when to reach for each — cures the piled-up cognitive load.

## 3. Information hierarchy

Skill content is **steps** (ordered actions) and **reference** (rules and facts consulted on demand), placed on a ladder by how immediately the agent needs them:

1. **In-skill step** — in `SKILL.md`, the primary tier.
2. **In-skill reference** — in `SKILL.md`, consulted on demand. A flat peer-set of rules is a fine arrangement, not a smell.
3. **External reference** — pushed to a linked file, loaded only when its pointer fires.

**Progressive disclosure** is the move down the ladder. The cleanest test is **branching**: inline what every branch needs; push behind a pointer what only some branches reach. A pointer's *wording*, not its target, decides whether the agent reliably follows it.

**Co-location**: a concept's definition, rules, and caveats live under one heading, so reading one part brings its neighbours.

## 4. Leading words

A **leading word** is a compact concept already living in the model's pretraining — *tight*, *red*, *fog of war*, *tracer bullet*, *forge* — that anchors a whole region of behaviour in the fewest tokens by recruiting priors the model already holds. It works twice: in the body it anchors execution (same behaviour every time the word appears); in the description it anchors invocation (shared language across prompts, docs, and skill fires it reliably).

Hunt for collapses: a quality restated three ways ("fast, deterministic, low-overhead") becomes one word (*tight*); a fuzzy gate ("a loop you believe in") becomes a binary observable (*red*). Every skill carries restatements a leading word retires.

## 5. Completion criteria

Every step ends on the condition that tells the agent the work is done. Make it:

- **Checkable** — the agent can tell done from not-done.
- **Exhaustive** where it matters — "every modified file accounted for", never "produce a change list".

A vague criterion invites **premature completion** — the agent's attention slipping from doing the work to being done. A demanding criterion is what forces **legwork**, whether the skill is steps or flat reference ("every rule applied" binds as hard as "every step done").

## 6. Difficulty asymmetry — the agent as learner

Skill text teaches the agent, and Matt's teaching asymmetry transfers whole:

> For acquiring knowledge, difficulty is the enemy. For skill acquisition, difficulty is the tool.

- **Reference sections = knowledge**: make them frictionless. Glossaries, co-location, leading words that recruit priors — difficulty here just eats the working memory needed for understanding.
- **Steps = skills**: make them demanding. Checkable, exhaustive completion criteria are the desirable difficulty that forces effortful, thorough execution.

## 7. ZPD set — only when the skill teaches a human

When the skill being forged is itself educational, spend interview time on:

- **Mission** — why the learner wants this. Ungrounded lessons feel abstract; the mission decides what to teach next.
- **Zone of proximal development** — the learner always challenged *just enough*: within reach, never trivial.
- **Fluency vs storage strength** — in-the-moment retrieval gives an illusory sense of mastery; long-term retention is the goal. Build storage via retrieval practice, spacing, and (for skills practice) interleaving.
- **Feedback loops** — every practice element gives feedback as immediately as possible, ideally automatically.

## 8. Socratic rules

The interview discipline, everywhere a skill talks to its user:

- **One question at a time.** Multiple questions at once are bewildering.
- **Recommended answer first**, every question — sparring partner, not blank slate.
- **Decisions are the user's; facts are looked up.** Anything the filesystem or tools can answer is never a question. An agent that answers its own questions has broken the interview.
- **Dependency order** — resolve the decision other decisions hang on first.

## 9. Style rules

- **Positive framing.** Steering by prohibition backfires — *don't think of an elephant* names the elephant. State the target behaviour; keep a prohibition only as a hard guardrail paired with what to do instead.
- **Single source of truth.** Each meaning lives in one authoritative place; changing behaviour is a one-place edit.
- **Vocabulary discipline.** Define terms exactly and list the near-synonyms to avoid ("say *seam*, not boundary") — consistent language is the whole point. Record **rejected framings** so future readers know what was considered and why it lost.
- **Cite the giants.** A borrowed concept names its source (Feathers' seams, Fowler's smells, Bjork's desirable difficulty) — never uncredited.
- **Prune relentlessly.** Sentence by sentence, run the no-op test — does this change behaviour versus the default? A failing sentence is deleted whole, not trimmed. Without this discipline every skill sediments.
