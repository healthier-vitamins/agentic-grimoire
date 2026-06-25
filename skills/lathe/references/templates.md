# lathe — forge templates

Three fill-in templates, one per tier. Fill every `[bracket]`. Delete sections that don't apply. Output the result in a single copy-paste block.

---

## Tier 1 — One-shot prompt

Use when there is no machine-checkable oracle, "done" is taste-based, or the task is bounded and a single (or few) call(s) suffice. Standards: role, explicit success criteria, XML-tagged sections, 3–5 diverse examples, chain-of-thought, self-check.

```
You are [role — an expert at the task; one sentence focuses tone + behavior].

<task>
[What to produce, and *why* it matters — motivation helps the model generalize.]
</task>

<context>
[Background, constraints, inputs. Reference real material the model needs.]
</context>

<success_criteria>
- [Criterion 1 — strict, no soft passes]
- [Criterion 2]
- [Criterion 3]
</success_criteria>

<examples>
[3–5 diverse input→output examples. Skip only if none are available.]
</examples>

Think step by step before answering.

<output_format>
[Exact shape: format, length, structure.]
</output_format>

Before finishing, verify your answer against every item in <success_criteria>. If any fails, fix it before responding.
```

> Drop aggressive phrasing ("CRITICAL: you MUST…") — current models over-trigger on it. Normal, direct instructions work better.

---

## Tier 2 — Workflow

Use when the path is predictable and multi-step but a full autonomous loop is overkill. Pick the shape that fits, then write the steps.

- **Prompt-chaining** — sequence where each step consumes the previous step's output. Best for a fixed pipeline.
- **Routing** — classify the input first, then dispatch to a specialized prompt. Best when inputs fall into distinct kinds.
- **Evaluator-optimizer** — one pass generates, a second pass critiques against criteria, repeat a *fixed*, small number of times. Best when iterative refinement against clear criteria adds measurable value (this is a bounded loop, not an open-ended one).

```
WORKFLOW: [chain | routing | evaluator-optimizer]

STEPS:
  1. [step] — input: [...] → output: [...]
  2. [step] — input: [output of step 1] → output: [...]
  3. [step] — input: [...] → output: [...]

CHECK BETWEEN STEPS: [what must be true to proceed; how to verify it]
```

If the steps start to need an unknown number of repeats against an oracle, promote to Tier 3.

---

## Tier 3 — Autonomous loop (`/goal`)

Use only when there is a machine-checkable oracle **and** the step count is unpredictable, the task repeats, or it needs end-to-end autonomy.

```
GOAL: [one objective] + [verifiable end state — what must be true to stop]

READ FIRST: [files / docs / issue / logs the loop must gather as context before acting]

EACH ITERATION:
  1. [run the verifier; read every failure]
  2. [pick the single highest-impact failure]
  3. [make the smallest change that fixes it]
  4. [re-run the verifier]

VERIFY (the gate):
  - Prefer deterministic: [tests / typecheck / lint / build / measurable threshold].
  - Hierarchy when no hard check exists: defined rules > visual feedback > LLM-as-judge.
  - Separate the checker from the maker — ideally a different model family. The maker grades itself too kindly.

STATE: keep a scratchpad of {done, failed, next} so a fixed mistake is never repeated.

STOP WHEN: [completion condition holds] OR [N iterations / token budget reached].
ON STOP: summarize what changed and what still fails.
```

### Runnable forms

**Claude Code**
```
/goal [verifiable end state, e.g. "every test in tests/auth passes, lint clean, no type errors, or stop after 8 turns"]
```
- Recurring on an interval (not run-until-done): `/loop 15m [prompt]` or self-paced `/loop [prompt]`.
- Unattended on a schedule / cloud / GitHub events: `/schedule [description]`.
- Deterministic per-turn gate: a `Stop` hook running `npm test && npx tsc --noEmit && npx eslint . --quiet`.

**Codex**
```
/goal Complete [objective] without stopping until [verifiable end state].
```
- Enable once: set `features.goals` in `config.toml` if `/goal` isn't listed.
- No native `/loop` (interval) or `/schedule` (cloud cron) — use a bash loop or GitHub Actions cron for those.

**Fallback (any host, no `/goal`)** — the bare Ralph loop:
```bash
while :; do cat PROMPT.md | <agent>; done   # PROMPT.md must carry the GOAL + VERIFY + "no placeholders" guard
```
Pair with an external iteration cap; this form has no built-in stop.

---

## Pitfalls checklist

Before shipping a loop, confirm each:

- [ ] **Oracle exists.** Tests / typecheck / lint / build / measurable threshold. No oracle ⇒ drop to one-shot + human review.
- [ ] **Stop condition is verifiable** and bans placeholder/stub "done" — guards against the Ralph-Wiggum premature-done failure.
- [ ] **Iteration/budget cap** set as a hard fallback alongside the completion condition. An unbounded goal never exits (scope/goal drift).
- [ ] **Checker ≠ maker.** Different model family if possible — models show self-preference bias and are poor at finding their own errors.
- [ ] **State persists** across iterations so corrected mistakes don't recur.
- [ ] **Economics sane.** Context re-bills ~O(n²); rely on prompt caching and track cost-per-accepted-change. Below ~50% accept rate, a loop costs more than doing it by hand.
- [ ] **Watch for reward hacking** — the model gaming the check while violating intent.

### Sources

- Anthropic, *Building Effective Agents* — the prompt → workflow → agent ladder, named patterns, stop conditions, cost/compounding-error caveats.
- Anthropic, *Building agents with the Claude Agent SDK* — agent loop (gather context → take action → verify → repeat); verification hierarchy (defined rules > visual > LLM-judge).
- Anthropic prompt generator + prompting best practices — role, success criteria, XML tags, 3–5 examples, chain-of-thought, self-check; dial back aggressive phrasing.
- Google Research (code migration), Airbnb Eng (test migration) — loops scale only where validation is a machine-checkable oracle.
- Google Research / self-correction papers — LLMs unreliable at finding their own errors → separate verifier.
- Geoffrey Huntley (*Ralph Wiggum*) + HumanLayer — the bare loop technique and its premature-done failure mode.
- OpenAI Codex docs — `/goal` (v0.128.0, Apr 2026; matured 0.141.0, Jun 2026), `features.goals` config flag.
