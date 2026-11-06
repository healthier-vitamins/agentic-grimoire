---
name: corkboard
description: Pin a pile of planning material (a chat export, spreadsheets, notes) to interactive boards (overview, timeline, decisions, kanban, moodboard) chosen to fit the data, with a Notion-style page per item. Every pin is evidence from the sources.
argument-hint: "[corpus files or links | an existing plan folder plus new material]"
disable-model-invocation: true
---

Goal: a **corkboard**, one page where a plan's items are pinned as cards, its numbers are drawn as charts, and each card opens into its own page (popup, then Expand to a full page, or New tab). The plan is shown on the boards its data earns, picked from a catalog of well-known formats in [`references/boards.md`](references/boards.md):

- **Overview**: the whole plan for whoever runs it. Headline numbers, a milestone strip, one tile per group with progress, next date and what's stuck.
- **Timeline**: a Gantt chart on a true date axis, empty stretches folded into marked breaks.
- **Decisions**: each open choice with its options, who backs which, and the thread behind it.
- **Kanban**: columns by state.
- **Flow**: phases in columns, groups in lanes, arrows for what waits on what.
- **Moodboard**: everything at once, each card wearing its evidence.

Every board zooms: far out it shows summaries, and a click on one zooms into it.

The code is fixed: `assets/` holds the boards, the item page and the charts; `scripts/build.py` combines them with the plan. Each run writes only data: `plan.json` and the evidence in `media/`. Scripts run from the folder holding `<plan-slug>/`, as `<skill-dir>/scripts/<name>.py`.

## Ground rule: provenance

Every pin traces back to the corpus or to a page the corpus names.

- **Pictures show the item's own subject**: a photo from the corpus; a screenshot of the item's own page (the venue, the listing, the review, the comment); a Wikimedia Commons photo of the landmark or place the item names, with credit and licence.
- **Charts draw numbers the corpus states**: prices, votes, counts, payments. A physical arrangement (seating, floor plan, route) appears as a screenshot of the venue's real plan.
- **An item without evidence carries no picture**, and what the corpus doesn't settle becomes a line in `gaps`.

The two misses this rule exists for, both from a trip board: generic photos pinned to items they weren't of (a dim sum shot on a banquet card, captioned "not the banquet"), and a "row 3" seating diagram drawn from a guess at the venue's layout. Both looked informative and told the reader nothing true.

`build.py` refuses a picture with no source, a screenshot or Commons photo with no URL, and a Commons photo with no credit or licence. Whether a picture shows *this* item is your check: view every image before pinning it.

## Paths

- **Build**: a corpus and no plan folder yet. Run steps 1–6.
- **Update**: an existing plan folder plus new material. Run [Update](#update).

## Steps

1. **Read the corpus.** Every file, every sheet tab, the whole chat export. Take only what bears on the plan; health details, addresses, codes and anything else personal stay out of `plan.json`.

   **Done when:** every source has been read end to end and is listed in `plan.sources` with the date it was read.

2. **Write `plan.json`** in `<plan-slug>/` under the current working directory, to the contract in [`references/plan-schema.md`](references/plan-schema.md). Every decision, booking, task and open question becomes an item. Copy facts as the source writes them (dates, prices, names); quotes are verbatim with who and when. Groups, icons, links between items and `onDay` mappings are your reading; keep a list of them for the hand-off.

   Mark the dates the plan turns on `milestone: true`, and every choice still being argued, or settled after argument, as a `decision` with its options and who backs each. These feed the Overview, Timeline and Decisions boards; an unmarked plan gets none of them.

   **Done when:** every actionable line in the corpus maps to an item or a gap, and every item field traces to a source line.

3. **Collect evidence** into `media/`, one `media/media.json` entry per file (fields in the schema reference):
   - Photos and videos in the corpus: `kind: "photo"` / `"video"`.
   - The item's own web page: `uv run --with playwright python -I <skill-dir>/scripts/capture.py <url> <plan-slug>/media/<key>.png [--selector CSS]`. It prints the entry's source fields. A page behind a login, a script wall or a bot check: screenshot it in a real browser (the Neko browser MCP where available).
   - A named landmark or place: a Commons photo, `kind: "commons"`, with credit, licence and the file page URL.

   Open every image. A cookie wall, an error page, a "no article by this name" page, or a different place is not evidence: recapture or drop it.

   **Done when:** every item that names a place, venue, listing or post has evidence pinned or a line in the hand-off saying why not, and every image has been viewed.

4. **Choose the charts.** 3–5 `dashboard` panels for the whole plan, plus `chart` blocks on the items whose numbers deserve one. A chart needs two or more comparable numbers or a part of a whole; a lone number is a `stat` or a tile. Follow the `dataviz` skill where it is installed.

   **Done when:** every value in every chart traces to a source line.

5. **Build and look.**

   ```sh
   uv run --with pillow python -I <skill-dir>/scripts/build.py <plan-slug>
   uv run --with playwright python -I <skill-dir>/scripts/check.py <plan-slug>
   ```

   `build.py` prints every rule break at once; fix them all and rebuild. It then prints the board ranking with each board's reason and builds the top four. Set `plan.boards` only to overrule the ranking, and say why in the hand-off. `check.py` shoots every built board, a popup and a full page at desktop (light) and phone (dark) into `<plan-slug>/check/`.

   **Done when:** `check.py` passes and every shot has been viewed with no overlapping cards, clipped labels or empty panels.

6. **Hand off.** Where an Artifact tool is available, publish `artifact.html` with any video files as supporting files at `media/<file>`, then rebuild with `--artifact-url <url>` and republish so New tab links resolve.

   **Done when:** the user has the folder path (and link), the boards built and why, the list of additions from step 2, every item left without evidence, and the gaps.

## Update

1. Read the new material and the current `plan.json`.
2. Change `plan.json`: new items, changed states, dates and prices, gaps the new material settles. Keep existing ids: saved card positions are keyed by them.
3. Run steps 3–6 for the changed items.

**Done when:** every change in the new material is in `plan.json` and listed in the hand-off, and the board is rebuilt and checked.

## Style

- **Accent**: one colour per plan, light and dark (`plan.accent`), taken from the plan's own materials where they have one (a wedding's palette).
- **Layout lives in the data**: the order of `groups`, `items` and `dashboard` arranges the boards. On Moodboard, readers drag cards to rearrange, and their moves stay in their browser. Boards whose positions encode data (Timeline's dates, Kanban's states) don't drag.
- **Visual style is fixed for now**: one design language with a per-plan accent. Board format is the choice that matters.
