---
name: sketchbook
description: Brainstorm and research the best UI/UX for any scenario (a trip plan, a wedding admin board, a CRM, a timetable). Ranks well-known interaction patterns against the workflow, studies real products when none fits, and hands back clickable drafts to compare, each checked against UX rules in a real browser.
argument-hint: "[the situation | files or a chat export | an existing plan folder plus new material | a repo or page to redesign]"
disable-model-invocation: true
---

Goal: drafts the user can click through and compare. Each draft is built on the **pattern** that fits the work. Style comes second.

A **pattern** is the arrangement the user acts through: a table, a kanban, a week grid, a map. Say *pattern*. *Board* means one of the plan-board route's boards. The catalog is [`references/patterns.md`](references/patterns.md).

## 1. Brief

Look up the facts before asking anything: the files, the repo, the chat export, existing mockups, memory. Write the brief:

- **Kind**:
  - *throwaway* is a one-off plan, read on a phone and shared.
  - *app* is something people come back to and change data in.
  - *site* is a page that strangers read.
- **Core job**: the action repeated most, as a verb on a noun ("assign a +1 to a guest", "find a free room on Tuesday").
- **Data shape**: each noun with a rough count, and which of these it carries: dates, states, places, people, money, a parent, a picture.
- **Who and how often**: the users, how often they use it, and on which device.

Ask only what the sources can't answer and what would change the pattern, the density or the medium. That is at most 4 questions, in one round, each with your recommended answer. Zero questions is the target. If you skip a question, write its answer into the brief as an assumption. Beyond the brief's four fields, the questions worth asking are:

- what the user must read at a glance on the landing view;
- whether a brand or design system already exists;
- accessibility needs (screen reader, low vision, one-handed phone use).

If the situation is a new idea with nothing to look up, suggest the user run `/grilling` (or `/grill-with-docs` inside a codebase with a glossary) first, then come back.

**Done when:** the brief is one paragraph naming the kind, core job, nouns with counts, frequency and device. Every fact names its source or is marked *assumed*.

## 2. Route

| The situation | Route |
|---|---|
| A plan built from a pile of material (chat export, sheets, notes) | The plan-board route in [`references/plan-boards.md`](references/plan-boards.md), formerly `corkboard`. It ranks its own boards and enforces provenance. Its hand-off is the report. Stop here. |
| Places to go near where someone stays, or an itinerary | `travel-field-guide`. Its hand-off is the report. Stop here. |
| A marketing, company or landing site | `design-taste-frontend`, given the brief. Stop here. |
| Anything else: an app, a throwaway template, a tool | Step 3. |

**Done when:** one route is chosen, and its reason quotes the brief.

## 3. Rank the patterns

Score every pattern in the catalog against the brief, using the catalog's scoring rule. Print the ranking as a table with columns for pattern, score, and a reason that quotes the brief. Pick the **primary** pattern, the one that carries the core job. Add up to two **secondary** patterns for the next-most-frequent jobs. An app almost always pairs its primary pattern with a record page.

If no pattern scores 7 or more, the catalog fits badly. Before drafting, look at 2 or 3 real products that do the core job, and note the arrangement each uses for it. Score that arrangement as an extra row, citing the products.

**Done when:** every catalog row has a score or a "ruled out by" reason, and the core job maps to exactly one primary pattern.

## 4. Draft

How many drafts:

- **Throwaway**: one draft on the primary pattern. List the runner-up patterns in the hand-off.
- **App**: three directions, and they must differ in the pattern or in density, not just palette.
  - A is the primary pattern, dense.
  - B is the primary pattern with a roomier record page.
  - C is the second-ranked pattern.
  - Run them through `huashu-design`. Give it the brief and the ranking, and have its three directions be A, B and C.

Every draft:

- **The core job works by clicking**, from the landing view, with the primary action on screen at both widths. Edit in place where the job is editing. Offer undo instead of confirm dialogs.
- **Real nouns**: use the user's own entities, labels and plausible counts from the brief. Include one record with an overlong name and one empty state that names the next action.
- **UX rules** come from the `ui-ux-pro-max` skill. Run its search for the product type with `--domain product`, then for the core job with `--domain ux`, and apply every rule that hits. Charts follow `dataviz`.
- **Medium**:
  - A throwaway is published as an Artifact, following `artifact-design`.
  - An app goes in the repo's `mockups/` folder, one HTML file per direction, plus an `index.html` linking them.

**Done when:** every draft exists, and in each one the core job runs end to end on the user's nouns.

## 5. Check

Open every draft in a real browser (Playwright, or the Neko browser MCP) at 1280 px and at 390 px. Do the core job by clicking, then screenshot each width and view each shot.

Then review each shot as a UX reviewer would. Go back through the `ui-ux-pro-max` rules from step 4 as a checklist, and check WCAG AA text contrast (4.5:1, 3:1 for large text) and tap targets of at least 44 px at 390 px.

**Done when:** for every draft at both widths, the core job completed and the shot was viewed, with no clipped text, overlaps, horizontal scroll or dead controls, and no failed UX rule, contrast or tap target. Fix any failure and recheck it.

## 6. Hand off

Give the user:

- The links or paths.
- The brief, with its assumptions.
- The ranking table.
- One line per draft naming its pattern and what it gives up.
- Your pick, with its reason.

Then stop for their pick. After they pick, an app is built in its codebase with `keystone-react` and `ui-ux-pro-max:ui-styling`.

**Done when:** the user has every item above, and nothing has been built past the drafts.
