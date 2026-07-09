# Slice Workspace Format

`<project>/.seam/` is the decomposition workspace. All slice state for this plan lives here:

```
.seam/
├── PLAN.md      # the original horizontal plan, verbatim — source of truth
├── SLICES.md    # the vertical decomposition: ordered slices + status
└── slices/      # one ticket per slice — created lazily on first write
```

## Bootstrap (first run)

1. `mkdir -p .seam`
2. Keep it out of git without touching the shared `.gitignore` — the decomposition is a private working aid:
   ```bash
   grep -qxF '.seam/' .git/info/exclude 2>/dev/null || echo '.seam/' >> .git/info/exclude
   ```
   (Not a git repo → skip; nothing to exclude from.)
3. Write `PLAN.md` from the ingested plan (Step 2).
4. `SLICES.md` and `slices/` are written once the cut is confirmed (Step 5).

## PLAN.md

The source plan, stored **verbatim**. Every slice traces back to it, so it is never edited by `seam` — if the plan changes, the user re-supplies it and the cut is redone.

## SLICES.md

The ordered decomposition and its live status. One row per slice, in build order:

```md
# Slices: {plan / feature name}

Source: PLAN.md

| # | Slice | Status | Ticket |
|---|-------|--------|--------|
| 0 | walking skeleton: one thread through every layer | pending | slices/0-walking-skeleton.md |
| 1 | {feature} end-to-end | pending | slices/1-{slug}.md |
| 2 | {feature} end-to-end | pending | slices/2-{slug}.md |
```

Status is one of `pending`, `active` (the user is building it now), or `done`. The user updates it as they work; a resume (Step 6) reads it to find the next `pending` slice.

## slices/<n>-<slug>.md

One ticket per slice. Numbered to match `SLICES.md`; slug is a short kebab-case name.

```md
# Slice {n}: {short title}

**Status:** pending

## Scope
{The one user-meaningful capability this slice delivers, end-to-end.}

## Layers touched
- {e.g. db: migration for X} → {api: endpoint Y} → {ui: component Z}

## Depends on
- {slice numbers this one builds on, or "none"}

## Acceptance check
- {How the user knows it's done — the runnable/observable outcome, e.g. "POST /x returns 201 and the row renders in the list view"}

## Source lines
- {which parts of PLAN.md fed this slice, so it's traceable}
```

Keep each ticket to a screen. The ticket describes *what* the slice is and how to know it's done — not *how* to write the code (that is the user's implementation, and skills like `keystone` govern it).
