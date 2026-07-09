# Slicing Heuristics — Horizontal → Vertical

How to re-cut a layer-organized plan into vertical slices. The goal is a sequence of slices that each **run and can be learned on their own**, in an order where every step leaves the system working.

## What a vertical slice is

A vertical slice is the **smallest user-meaningful capability that runs end-to-end through every layer it needs** — data → backend → API → frontend → test — for **one** feature. Not "the API for everything"; "everything for one feature."

Contrast:

- **Horizontal (what plans usually give you):** Phase 1 builds all endpoints, Phase 2 builds all UI. Nothing is exercisable until Phase 2. A 40-file chunk lands with no way to run it.
- **Vertical (what `seam` produces):** Slice 1 is *one* feature from DB migration to rendered UI. It runs. You can review it, ship it, and learn it before slice 2 starts.

## The cut

1. **Group by feature/entity, not by layer.** Read the plan's horizontal phases and pull the rows belonging to *one* feature out of *each* phase. Those rows, stitched together top-to-bottom, are one slice.
2. **Walking skeleton first.** Slice 0 is the thinnest possible thread that touches every layer end-to-end — even if it does something trivial (one hardcoded field round-tripping DB→API→UI). Its job is to prove the wiring and stand up shared scaffolding, so every later slice plugs into a working spine.
3. **Order by dependency, then by value.** After the skeleton, sequence slices so each only depends on slices already built. Among independent slices, put the higher-value or higher-risk one first.
4. **Handle shared scaffolding explicitly.** Infrastructure several slices need (auth, a base model, a client wrapper) goes into the walking skeleton or the first slice that needs it — never a big up-front "build all the scaffolding" phase, which is just another horizontal layer.
5. **Keep slices small.** Each should be independently reviewable, runnable, ideally shippable, and small enough to understand in one sitting. If a slice spans many features or can't be run until another lands, split it.

## Every slice should be able to answer

- **Does it run end-to-end on its own?** If it needs a not-yet-built slice to be exercisable, reorder or merge.
- **Is there an acceptance check?** A runnable or observable outcome that says "done" (a passing test, an endpoint returning the right shape, a row rendering).
- **Does it trace to the plan?** Every slice's work comes from `PLAN.md`; nothing invented, nothing dropped.

## Smells

- **A slice named after a layer** ("the API slice") — that's a horizontal phase in disguise. Re-cut by feature.
- **Slice 1 can't run without slice 3** — dependency order is wrong; reorder or fold together.
- **A giant "setup" slice** — fold the scaffolding into the walking skeleton or the first feature that needs it.
- **A slice too big to review in one sitting** — split along a natural feature/sub-feature seam.
