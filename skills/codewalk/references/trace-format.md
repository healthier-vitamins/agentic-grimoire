# Trace format

Sweep gear's unit of delivery. A **chain** is one end-to-end causal path through the
target. A **step** is one atomic unit inside a chain. Say *chain* and *step* — not flow,
hop, pass, or concern. (Rejected framings: *flow/hop* — vivid for call chains, wrong for a
guard clause or a CSS rule; *concern* — watermark's word for a bucket of changed lines,
where a chain is an ordered path through unchanged ones.)

Ported from the `watermark` skill, which decomposes a diff into atomic commits. Sweep
decomposes existing code into atomic steps and writes nothing to it.

## Finding the chains

1. Fix the target's entry points: exported symbols, route handlers, event handlers, CLI
   commands, or the changed lines of a diff.
2. From each entry point, follow call and data flow until it leaves the target or
   terminates.
3. Two entry points that never converge are two chains. One entry point fanning into
   independent branches (a switch over commands, a route table) is one chain per branch.

**The chain gate.** One chain → trace it. Two or more → stop before any step, show the
chain map, and ask which the user wants first (`AskUserQuestion`). Write every chain to
`.codewalk/sweep/chains/` before asking, so the answer costs no re-detection. This gate
and the "next" between parts are the only things sweep asks — no comprehension questions.

```
Trace of: apps/partner-web/src/pages/search — 3 chains

1. query submit → API → render        SearchPage.tsx:88    6 steps
2. error surfacing → field + button   SearchPage.tsx:141   4 steps
3. back-navigation re-run             useSearch.ts:74      3 steps
```

## What makes one step

- **The "and" test.** A why-line reaching for "and" is two steps. Split at the conjunction.
- **Always-split triggers** — fire regardless of how "one thing" the code feels:
  - A definition and its call sites → separate steps.
  - The happy path and the error or edge path → separate steps.
  - A type, schema, or config value and the logic consuming it → separate steps.
- **Bias to split.** Unsure whether two lines are one step or two → two steps.
- **Logical unit, not line count.** A step spans as many lines as its one idea needs;
  splitting a coherent function mid-thought teaches nothing. Where this rule and
  bias-to-split conflict, split wins — it only prevents per-line over-splitting.

## Step shape

````
step 2/6 — useSearch.ts:31 — debounce the query

```ts
const debounced = useDebounce(query, 300)
```

A keystroke-per-request search burns the API quota.

- The hook holds the last value for 300ms
- The timer resets on every keystroke
- An empty query short-circuits before the fetch
````

- **Header** — `step N/M — path:line — imperative summary`, ≤50 chars where possible.
- **Excerpt** — the lines the step is about plus minimal context, in a chat code block.
  Code before gloss, every time (Sweller's worked-example effect).
- **Why-line** — ≤72 chars, the takeaway. The reader who stops here still has the point.
- **Bullets** — `-`, one idea each, cap five, wrap 72. A bullet reaching for "and", "so",
  or "because" is two bullets. Active, simple present, name the actor.
- **The cut** — draft complete, then subtract. Delete whole any bullet that re-says the
  header, glosses ("essentially"), hedges ("robust"), or narrates ("this step shows").
  The floor: the *why*, and any fact that changes how the next step reads.
- A step whose why the header already carries ships as header plus excerpt alone.
- One connective line ties the step to the previous step or a `reference/glossary.md` term.
- **Improve-line** — at most one trailing line, `improve — <the suggestion>` (≤72 chars),
  only when the excerpt holds a change you would genuinely flag in code review — most
  steps hold none, and silence is the norm. Your own knowledge decides what counts; no
  taxonomy. It is a note, not a task: sweep stays read-only, the line changes nothing.

## Chain files

`.codewalk/sweep/chains/NNNN-slug.md` — sequential numbering, scan for the highest and
increment. Created lazily at the first chain gate.

```md
---
Status: pending | traced
Date: {YYYY-MM-DD}
Entry: {file:line symbol}
Detected-from: {the sweep target}
---

# Chain: {the name shown in the chain map}

{Why it was deferred, or the date it was traced.}

- {file:line} — {step summary}
```

Write the step list at detection time, before the user picks. On tracing a chain, flip
`Status: traced` rather than deleting it — the traced set is the coverage record — and
append each improve-line the trace flagged under the step list, one per line:
`- improve: {file:line} — {suggestion}`. Offer `pending` chains as targets at the next
session's scope step.
