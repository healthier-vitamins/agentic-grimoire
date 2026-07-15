---
name: skillsmith
description: Forge a new skill or audit an existing one, in Matt Pocock's style.
argument-hint: "[skill idea | path to existing SKILL.md]"
disable-model-invocation: true
---

# Skillsmith

Forge skills the way Matt Pocock does: **grill first, write second**. A skill is forged from decisions the user makes, not prose the agent improvises — the interview is the anvil, the draft is what comes off it.

Read [`references/style.md`](references/style.md) before either branch — it is the standard every question, derivation, and audit below measures against.

## Branch selector

- The argument is a path to an existing `SKILL.md`, or names a skill that exists on disk → **Audit branch**.
- The argument describes something new (or is empty) → **Forge branch**.
- Genuinely unclear which → ask, one line.

---

## Forge branch — create a new skill

### Step 1 — Look up the facts

Facts are looked up; only decisions are asked. Before any question, gather from the environment:

- The target repo's skill conventions: where skills live, frontmatter shape, `references/` layout. Read one or two existing skills as exemplars.
- Name collisions: existing skills whose name or triggers overlap the idea.
- Prior art: an existing skill that already covers part of the idea (reuse beats rewrite).

**Done when:** you can state the target directory, the frontmatter fields the repo uses, and any collision — without asking the user any of it.

### Step 2 — Grill (5 questions, hard cap)

Interview the user one question at a time, each with your recommended answer first, in this dependency order. An adaptive follow-up is allowed but **spends a slot** — five questions total, then stop.

1. **Purpose + leading word** — what the skill does in one sentence, and the single pretrained concept that anchors it (*forge*, *triage*, *fog of war*). Propose a candidate.
2. **Invocation** — model-invoked (agent can fire it; description costs context load every turn) or user-invoked (zero context load; the user's memory pays cognitive load). Recommend user-invoked unless the agent or another skill must reach it autonomously.
3. **Branches** — the genuinely distinct ways the skill gets used. Each branch earns a trigger and shapes disclosure.
4. **Content shape + completion criteria** — steps, reference, or a mix; and for each step, what checkable condition means *done*. Push for exhaustive criteria ("every X accounted for"), never vibes ("looks good").
5. **Wildcard** — whatever the answers above left genuinely unresolved. If the skill teaches a human, spend this slot on the ZPD set in `style.md` §7 (mission, fluency vs storage, retrieval/spacing).

**Done when:** all five slots are resolved or the user says proceed. Decisions the user declined to make fall to your recommendations — say so in the draft review.

### Step 3 — Derive

Settle the remaining design yourself, from the answers:

- **Disclosure** — inline in `SKILL.md` what every branch needs; push behind a `references/` pointer what only some branches reach.
- **Description** — model-invoked: front-load the leading word, one trigger per branch, zero synonym padding. User-invoked: one human-facing line.
- **Difficulty calibration** — reference sections frictionless (glossary, co-location, leading words); steps demanding (completion criteria that force legwork).

### Step 4 — Draft + self-prune

Write the full draft, then prune it against `style.md`:

- Run the **no-op test** on every sentence: would the agent behave this way anyway? Delete the sentence, keep no residue.
- Reframe every prohibition as the positive behaviour; keep a bare "don't" only as a hard guardrail with an "instead" beside it.
- Hunt **leading-word collapses**: any triad or restated quality becomes one pretrained word.

**Done when:** every remaining sentence changes agent behaviour, and every step ends on a checkable completion criterion.

### Step 5 — Draft review

Present the complete draft plus one line of rationale per *derived* decision (disclosure placement, description, calibration). The user corrects here — edits, not another interview. Write the files only on their confirmation, following the conventions found in Step 1.

---

## Audit branch — improve an existing skill

### Step 1 — Read

Read the target skill in full — `SKILL.md` and every file it points to — plus [`references/audit-rubric.md`](references/audit-rubric.md).

**Done when:** `SKILL.md` and every file it points to have been read, plus the rubric.

### Step 2 — Audit

Walk **every rubric row** against the skill. Report findings ranked most-damaging first:

```
[failure mode] path:line — what's wrong → proposed fix
```

**Done when:** every rubric row is marked clear or flagged — the audit accounts for the whole rubric, it doesn't stop at "found some issues."

### Step 3 — Pick + grill

The user picks which findings to fix. Grill only where a fix is a genuine decision (which leading word, whether to split a skill) — usually 0–2 questions, recommended answer each.

### Step 4 — Apply

Apply the picked fixes and show a summary of what changed per finding.
