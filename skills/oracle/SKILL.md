---
name: oracle
description: Descend one stack vertically — surface and teach the unknown-unknowns beneath a prompt.
disable-model-invocation: true
---

Goal: surface what the user does not know they don't know — the gaps beneath the prompt ("unknown unknowns", Rumsfeld) — and teach each one deep enough to stick.

Companion to `compass` (breadth across competing approaches). `oracle` descends one stack vertically.

## Steps

1. **Restate + infer intent.** Restate the prompt and state its underlying intention in one line.

2. **Assume zero prior knowledge.** Anything the prompt does not mention, treat as unknown to the user and worth surfacing.

3. **Descend.** List the concepts, constraints, trade-offs, prerequisites, and failure modes the prompt never touches. For each gap, ask what lies beneath it — the concept it presupposes, the mechanism it hides, the failure mode it papers over — and recurse.

   Example descent: connection pooling → connection lifecycle → TCP handshake cost → file-descriptor limits → why the pool-size default exists.

   **Done when:** every gap bottoms out at first principles or a layer the prompt shows the user already knows.

4. **Research.** `WebSearch` for what practitioners actually do; `Context7` MCP for library/framework/API documentation. Rank sources by `../../.shared-agents/common/source-priority.md` — read it before searching.

   **Done when:** every claim in step 5 carries a source.

5. **Teach each gap:**
   - **What it is** — one line.
   - **Why it matters here** — the consequence for this task.
   - **What breaks if ignored** — the failure the user would hit.

   Each claim cited. Add up to 2 further-reading sources (documentation preferred) only when a gap needs deeper reading.

## Output shape

- **Intent** — one line.
- **Descent map** — each gap with the chain beneath it.
- **Per gap** — the three teach lines from step 5, cited.
