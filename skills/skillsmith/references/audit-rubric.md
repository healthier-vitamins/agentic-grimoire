# Audit rubric

One row per failure mode. Walk **every** row against the target skill; mark each clear or flagged. Each row: **Trigger** (where to look) / **Smell** (what the defect looks like) / **Fix**. Failure modes and their cures are defined in [`style.md`](style.md); rows cite the section.

## Premature completion — §5

- Trigger: every step's closing line.
- Smell: no completion criterion, or an uncheckable one ("make sure it's good", "review thoroughly").
- Fix: rewrite as a checkable, where-it-matters exhaustive condition ("every rubric row marked clear or flagged").

## Duplication — §9

- Trigger: any meaning appearing in more than one place — body vs description, two sections, skill vs its references.
- Smell: the same rule or definition restated; editing the behaviour would take a two-place edit.
- Fix: keep the single source of truth, point at it from the other site.

## Sediment — §9

- Trigger: lines referencing tools, paths, flags, or workflows.
- Smell: references to things that no longer exist or no longer apply — stale layers left because removing felt risky.
- Fix: verify each referent still exists; delete the layer if it doesn't.

## Sprawl — §3

- Trigger: overall `SKILL.md` length.
- Smell: too long even with every line live — reference material every branch drags along, steps for paths most runs skip.
- Fix: disclose reference behind pointers; split by branch or sequence so each path carries only what it needs.

## No-op lines — §9

- Trigger: every sentence, tested in isolation.
- Smell: the agent would behave this way anyway ("be thorough", "think carefully") — load spent saying nothing.
- Fix: delete the sentence whole; if the intent was real, replace with a stronger leading word, not more adverbs.

## Negation steering — §9

- Trigger: "don't", "never", "avoid" outside hard guardrails.
- Smell: behaviour steered by prohibition, the banned thing named and made more available.
- Fix: state the positive target behaviour; keep the prohibition only as a guardrail paired with an "instead".

## Weak or missing leading words — §4

- Trigger: multi-clause restatements, fuzzy quality gates, descriptions spending sentences to gesture at one idea.
- Smell: "fast, deterministic, low-overhead" where *tight* would do; no single concept anchoring the skill's behaviour.
- Fix: collapse into one pretrained word; repeat it where the behaviour should recur.

## Mis-ranked disclosure — §3

- Trigger: what sits inline in `SKILL.md` vs behind pointers.
- Smell: material only one branch reaches sits inline (bloat), or material every run needs hides behind a pointer (hidden essentials). Related: a concept's rules scattered across headings instead of co-located.
- Fix: apply the branch test — inline what every branch needs, push down what only some reach; gather scattered rules under one heading.

## Description defects — §2, §4

- Trigger: the frontmatter `description`.
- Smell: synonym-padded triggers (one branch phrased three ways), identity prose restating the body, leading word buried mid-sentence. For user-invoked skills: model-facing trigger lists nobody will ever match against.
- Fix: front-load the leading word; one trigger per genuine branch; user-invoked descriptions become one human-facing line.

## Wrong invocation mode — §2

- Trigger: the `disable-model-invocation` frontmatter (or its absence).
- Smell: a skill only ever fired by hand paying context load as model-invoked; or a skill other skills must reach locked user-invoked.
- Fix: flip the mode to match who actually needs to reach it.

## Missing vocabulary discipline — §9

- Trigger: skills that define or depend on terms of art.
- Smell: a term used inconsistently, near-synonyms drifting in, no "avoid" guidance, borrowed concepts uncredited.
- Fix: define each term once, list the synonyms to avoid, cite the source of borrowed concepts.
