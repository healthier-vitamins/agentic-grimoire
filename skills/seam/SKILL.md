---
name: seam
description: Re-cut a horizontal, layer-by-layer plan into vertical slices — one feature threaded end-to-end (scaffold→backend→API→frontend→test) — and emit them as ordered, stateful tickets you implement yourself. Never writes project code. Use on "seam", "vertical slice", "slice this plan", or when a plan is organized by layer (all API, then all UI) and you want feature-by-feature tickets instead.
argument-hint: "[plan-path]"
disable-model-invocation: true
---

Goal: take a plan that is organized **horizontally** (Phase 1 = the whole API, Phase 2 = the whole UI) and re-cut it **vertically** — one user-meaningful feature threaded end-to-end through every layer it needs — then hand back an ordered set of slice tickets. A vertical slice runs and can be reviewed and learned on its own; a horizontal phase is a large chunk that exercises nothing until the next phase lands. Companion to `lathe`, which decides a task's *shape* upstream; `seam` assumes a plan already exists and only re-cuts it.

**Iron rule: never modify project files.** `seam` decomposes and tickets work — it does not implement it. The only writes are inside `.seam/` and `.git/info/exclude`. The user builds each slice themselves.

Run the steps in order.

## Step 1 — Load the workspace

Read `.seam/`: `PLAN.md`, `SLICES.md`, and every ticket under `slices/`. This is a **stateful** request — the decomposition persists across sessions and the user marks slices done as they build.

- No workspace → bootstrap per [references/workspace-format.md](references/workspace-format.md).
- Workspace exists → this is a resume; jump to Step 6.

**Done when:** existing slice state is loaded, or the workspace was just bootstrapped.

## Step 2 — Ingest the plan

Fix exactly one source plan. Priority:

1. **User named a path** (the `[plan-path]` arg) → read it verbatim.
2. **A plan was just produced** in this session (plan mode, a pasted plan) → use it.
3. **Ambiguous** — nothing named and nothing in hand → `AskUserQuestion` for the plan's location or ask the user to paste it. Never invent a plan.

Store it verbatim as `.seam/PLAN.md` — it is the source of truth the slices trace back to.

**Done when:** the original horizontal plan is captured in `.seam/PLAN.md`.

## Step 3 — Re-slice (horizontal → vertical)

Apply the heuristics in [references/slicing.md](references/slicing.md): group the plan's work by feature/entity across **all** layers, then order the slices with the **walking skeleton first** — the thinnest thread that touches every layer, proving the wiring before any feature is fleshed out.

Every unit of work in `PLAN.md` must land in exactly one slice. Nothing dropped, nothing built twice.

**Done when:** each unit of the plan maps to exactly one ordered slice.

## Step 4 — Confirm the cut

Before writing final tickets, show the ordered slice list and use `AskUserQuestion` (or a plain confirm) to let the user **reorder, merge, or split** slices. The cut is a judgment call — do not commit tickets the user hasn't seen.

**Done when:** the user approves the slice order.

## Step 5 — Emit tickets and stop

Write the decomposition into `.seam/` per [references/workspace-format.md](references/workspace-format.md):

- `SLICES.md` — the ordered slice list with a status column (`pending` / `active` / `done`).
- `slices/<n>-<slug>.md` — one ticket per slice: scope, layers touched, dependencies, and an acceptance check (how the user knows the slice is done).

Then present the ordered list and **stop**. The user implements each slice; `seam` writes no project code.

**Done when:** all tickets are written and the ordered slice list is shown.

## Step 6 — Resume

On re-invocation with an existing workspace: report each slice's status from `.seam/` rather than re-slicing from scratch, and point at the next `pending` slice. Support editing the decomposition as the plan evolves — add a slice, or split/merge existing ones (renumber `SLICES.md` and the `slices/` tickets to match), always reconfirming a changed cut per Step 4.

**Done when:** current slice status is reported and any requested edits to the cut are applied and reconfirmed.
