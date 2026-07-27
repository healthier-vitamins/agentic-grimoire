---
name: oracle
description: Descend one stack vertically — surface and teach the unknown-unknowns beneath a prompt.
disable-model-invocation: true
---

Goal: surface what the user does not know they don't know — the gaps beneath the prompt ("unknown unknowns", Rumsfeld) — and teach each one deep enough to stick.

Companion to `compass` (breadth across competing approaches). `oracle` descends one stack vertically.

**When not to use:** for open exploration — "how do I", "what is", general research — the bare harness is the better default; it plans its own approach and reads more cohesively than a fixed procedure. Reach for `oracle` when committing to a design in an unfamiliar domain and the risk is a gap you cannot name.

## Steps

0. **Misfit check.** `oracle` misfits when the prompt is a factual lookup with a determinate answer — "what is X", "what's the syntax for Y", "does Z support W". Nothing is being committed to, so there is nothing to descend *toward*. That is the whole test; apparent simplicity is **not** a misfit, since a short prompt preceding a real decision is exactly where gaps hide.

   On misfit, name the absent trigger in one line, then answer directly and skip the rest:

   > Skipping `oracle`: factual lookup with a determinate answer — no pending design commitment to descend toward. Answering directly.

1. **Restate + infer intent.** Restate the prompt and state its underlying intention in one line.

2. **Calibrate depth, not scope.** Read the prompt's vocabulary for the level the user works at, and let it set *how much explanation each gap gets* — never which gaps you reach. Fluency at one layer says nothing about the layers beneath, so calibration must not prune step 3's descent. Descend fully; explain briefly where the user is plainly fluent.

3. **Descend.** List the concepts, constraints, trade-offs, prerequisites, and failure modes the prompt never touches. For each gap, ask what lies beneath it — the concept it presupposes, the mechanism it hides, the failure mode it papers over — and recurse.

   Example descent: connection pooling → connection lifecycle → TCP handshake cost → file-descriptor limits → why the pool-size default exists.

   Aim: every gap bottoms out at first principles or a layer the prompt shows the user already knows.

4. **Research.** `WebSearch` for what practitioners actually do; `Context7` MCP for library/framework/API documentation. Rank sources by [`references/source-priority.md`](references/source-priority.md) — read it before searching. Cite what is non-obvious, contested, or version-specific; undisputed statements need no footnote.

5. **Teach each gap:**
   - **What it is** — one line.
   - **Why it matters here** — the consequence for this task.
   - **What breaks if ignored** — the failure the user would hit.

   Add up to 2 further-reading sources (documentation preferred) only when a gap needs deeper reading.

   Aim: every gap in the descent map is taught. Depth on the gap that decides the user's next move beats even coverage — the three lines are a default frame, not a quota to fill evenly.

## Output shape

A default, not a template — reshape when the material calls for it.

- **Intent** — one line.
- **Descent map** — each gap with the chain beneath it.
- **Per gap** — the three teach lines from step 5, cited per step 4.
