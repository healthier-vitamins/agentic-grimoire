---
name: orrery
description: Turn one formula into an explorable explanation — an interactive page where every symbol is a control and the result moves as you drag.
argument-hint: "[formula, slide screenshot, or concept name]"
disable-model-invocation: true
---

Goal: build an **explorable explanation** (Bret Victor, *Explorable Explanations*, 2011) of one formula. Every input is something the reader drags; every output visibly moves; the mechanism behind the symbols is seen instead of taken on trust.

The reader is a **newcomer**: they hold the formula (often a lecture-slide screenshot) and lack the intuition behind it. Every word on the page is written for them.

## Ground rule: code draws

Every curve, point, length, angle, region, and label position is computed at runtime by the page's own JavaScript from the formula's functions. You write the functions (`f`, `df`, `term(n)`, …) and a world-to-screen mapping; the page samples and draws. Every number shown on the page is likewise computed by that code. A coordinate, SVG path string, or result typed by hand into the HTML is a bug — replace it with a call to the math.

Keep the math in one `<script id="math">` block of pure functions that touch no DOM, so step 7 can lift it out and run it.

## Step 0: Ensure the dependencies are installed

Step 6 reads two skills' files directly (both are user-invoked, so the Skill tool cannot fire them). Look for each directory in `~/.claude/skills/`, `~/.agents/skills/`, or the active profile's `skills/`, and record its absolute path:

- **`scribe`** (this repo's): `SKILL.md` plus `references/ai-tells.md`.
- **`wait-what`** (Matt Pocock's): `SKILL.md`.

For each one missing, show its install command and **ask before running it** — it mutates the global skill store:

```sh
npx skills add healthier-vitamins/agentic-grimoire -g -s scribe
npx skills add mattpocock/skills -g -s wait-what
```

If the user declines, continue and write step 6 in ASD-STE100 Simplified Technical English without the scribe pass; say so in the hand-off.

**Done when:** both paths are recorded, or the decline is noted.

## Steps

1. **Read the formula.** From `$ARGUMENTS` (or ask for it), list every symbol with a plain-English meaning and a role: **control** (the reader drags it), **computed** (the page derives it), or **fixed** (a constant). A slide carrying several linked formulas (tangent, normal, "perpendicular if …") is one page; read them all.

   **Done when:** every symbol in every formula has a meaning and a role, and every computed symbol names the formula that produces it.

2. **Pick the view.** Place the formula in one branch, then read that branch's recipe in [`references/views.md`](references/views.md):
   - **Geometric** — it has a shape: slopes, tangents, areas, vectors, trig.
   - **Process** — a rule that runs over steps or time: sums, limits, interest, recursion.
   - **Machine** — inputs map to an output with no useful shape: probability, averages, conversions.

   **Done when:** every control from step 1 is a widget (slider, drag handle, toggle) and every computed symbol is something visible that moves when a control moves.

3. **Pick the starting example.** Open on the textbook's first example: y = x² at a = 1; one fair die; 5% for 10 years.

   **Done when:** the page shows the example on load, and its numbers can be checked by hand in under a minute.

4. **Hunt the edge cases.** Every condition attached to the formula — each "if", "≠", "> 0", domain limit, or "for all n" — gets a button that jumps the controls to where the condition bites. Controls snap onto the exact edge value, so a slider lands on it too. Beside it, one sentence says what breaks there (a 1 ÷ 0, a vertical line, a sum that diverges) and what still holds.

   **Done when:** every condition in the source has a jump button and its sentence.

5. **Build the page.**
   - **One color per symbol**, the same in the formula text and the drawing, paired with a second cue (solid vs dashed, a label) so it reads without color.
   - **Substitution panel**: each formula in three rows — the general form, the current numbers plugged in, the simplified result.
   - **Predict, then reveal**: one moment on the formula's central idea where the reader commits a guess (drag a ghost line, pick an option) before the page shows the truth and compares the two.
   - **Challenges**: 2–3 tasks at the end ("find an *a* where the normal slope is −1/4"), each checked live with a visible tick; at least one lands on an edge case from step 4.
   - **Typeset math in HTML**: italic serif from Google Fonts (STIX Two Text) and CSS fractions. The artifact sandbox blocks external stylesheets, so KaTeX and MathJax CSS fail to load there.

   **Done when:** moving any control updates the drawing, every panel row, and every challenge check, with no stale value anywhere.

6. **Write the notes.** One short section per *why* the formula raises: what each part is, why it takes this form, why the condition exists. Draft them, then edit the draft against both recorded skills: scribe's `SKILL.md` and its `references/ai-tells.md` cleanup pass, then `wait-what`'s Simplified Technical English. The newcomer is scribe's one reader, and the source's own notation is the ubiquitous language — keep the slide's `f′(a)`, and define any new name (like *m*) the first time it appears. Where the picture shows cases without proving the formula, say so in one sentence.

   **Done when:** every section answers one named *why*, both passes have run, and the proof caveat sits wherever it applies.

7. **Check the numbers in code.** Write a Node script (in the scratchpad) that extracts `<script id="math">` from the page and evaluates every computed symbol at three points: the starting example, one edge case, and one random point. Compare each against an independent computation — the hand-checked numbers from step 3, a numerical derivative against `df`, a dot product of 0 for perpendicular lines, a brute-force sum against a closed form.

   **Done when:** every computed symbol matches at all three points to the page's displayed precision, and the script's output is shown to the user.

8. **Ship.** Save the page as `<formula-slug>.html` in the current working directory, then publish the same file as an artifact when the Artifact tool is available.

   **Done when:** the user has the file path, the link (when published), and one line naming what to drag first.
