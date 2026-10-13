# Views

One recipe per branch. Read only the branch step 2 chose. Every recipe obeys the ground rule in `SKILL.md`: code samples and draws, nothing is typed by hand.

## Geometric

The formula has a shape. Draw it on graph paper the reader can drag across.

- **One scale for both axes.** A single pixels-per-unit constant maps world to screen (y flipped), so a right angle looks like one and a 45° slope looks like 45°.
- **Sample curves** at 400 or more points across the window; clamp y to the window plus a margin and clip the drawing group.
- **Draw lines from a direction vector.** Through point P, extend far along the unit vector (1, m)/√(1+m²) and clip. A perpendicular is the same vector turned 90°, (−m, 1)/√(1+m²) — this draws the vertical case (m = 0) with no special branch.
- **Mark the relationship the formula is about** on the drawing itself: a right-angle square for perpendicular, a shaded rise/run triangle for slope, a filled region for area or integral, an arrow for a vector.
- **Place labels in free space** by computing the directions marks occupy and putting each label in a quadrant nothing else uses; give labels a background-colored halo (`paint-order: stroke`).
- **Drag on the plot** as well as the slider: pointer events with `touch-action: pan-y`, so the page still scrolls on a phone.
- **Drawing method:** plain SVG from the page's own script. Reach for JSXGraph (pinned, from cdnjs) only for many linked constructions or 3D, and inline its CSS.

## Process

The formula is a rule that runs over steps or time. Let the reader run it one step at a time.

- **Step controls:** Step, Play, Reset, plus a slider for *n* or *t*.
- **Each step leaves a trace:** a row appended to a table and a mark added to the picture (a bar per partial sum, a stair per recursion, a point per period of growth).
- **Show the target:** draw the limit, closed form, or threshold as a line, so convergence, overshoot, or blow-up is seen against it.
- **Keep the history visible:** the reader should be able to point at the row where the behaviour changes.
- Under `prefers-reduced-motion`, Play advances steps without animated transitions.

## Machine

Inputs map to an output with no useful shape. Show where the output comes from.

- **One slider per input**; the output as a large number with a live breakdown of each term's contribution (a stacked bar, or the term-by-term sum written out).
- **Probability:** draw the sample space as a grid of outcomes with the favourable ones filled. Add a "simulate 1,000 trials" button run by code, plotting the running frequency as it closes in on the formula's value.
- **Conversions and rates:** write the unit chain and strike each unit as it cancels.
