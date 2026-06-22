---
name: oracle
description: Infer the prompt's intent and surface unknown-unknowns — concepts the prompt never mentions that the user likely doesn't know. Use on "oracle"/"brainstorm" or when exploring an unfamiliar topic.
---

Goal: surface what the user does not know they don't know.

Companion to `compass` (which explores breadth across competing approaches). `oracle` explores one stack vertically — depth, unknown-unknowns.

## Steps

1. **Restate + infer intent.** Restate the prompt and state its underlying intention in one line.

2. **Assume zero prior knowledge.** Treat anything NOT mentioned in the query as unknown to the user. If it wasn't written, assume they don't know it — so it is worth surfacing.

3. **Find the gaps.** List the concepts, constraints, trade-offs, prerequisites, and failure modes the prompt never touches. These are the unknown-unknowns. Name them so the user learns they exist.

4. **Research before surfacing.**
   - `WebSearch` for landscape, current context, and what practitioners actually do.
   - `Context7` MCP for library/framework/API documentation and syntax.
   - Rank sources by `../../.shared-agents/common/source-priority.md` — read it before searching, and cite the source per claim.

5. **Per gap, give 2 sources framed as a verdict:** one for *why it's good*, one for *why it's not good*. Let the user weigh both sides.

6. **Optionally add up to 2 further-reading sources** for the suggested topic — only if deeper understanding is required. Prefer documentation for reading on the topic and for syntax reference. If the two why-good / why-not sources already suffice, skip this.

## Output shape

- **Intent** — one line.
- **Gaps / unknown-unknowns** — bulleted list.
- **Per topic:**
  - 2 sources: why-good / why-not.
  - Up to 2 optional further-reading sources (documentation preferred) when deeper reading is warranted.
