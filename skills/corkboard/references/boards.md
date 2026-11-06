# Board catalog

Each board is a well-known way to lay out a plan, drawn by one fixed file in `assets/`. A board
is offered only when the plan holds the data it draws. `build.py` encodes the rules below in its
`BOARDS` registry, prints the ranking on every build, and builds the top four unless `plan.boards`
names them.

Scores run 0 to 10 and measure the share of items the board can place well, so a board that would
leave most cards in a "No date" gutter ranks low however many dates the rest have.

| Board | Known as | Draws | Offered when | Score | Ruled out by |
|---|---|---|---|---|---|
| `overview` | Portfolio or program view (Asana Portfolios, Jira Plans, a PM's status page) | Headline numbers, a milestone strip from today to the event, one tile per group with progress, next date, stuck count and every item as a row | 10 or more items, or 4 or more groups | 10: the anchor of any large plan | A plan small enough to read as one list |
| `timeline` | Gantt chart (MS Project, Linear roadmaps, TeamGantt) | A section per group on a true date axis; each item's name over its mark (an outlined bar with its dates for a span, a diamond for a milestone, a ring for a due date); today is the one accent and lateness the one red; undated items listed below; opens at 100% on today | 4 or more dated items | dated share × 10, plus milestones (up to 5) | Mostly undated plans: they'd sit in the undated list |
| `decisions` | Decision log or RFC thread (Notion decision DB, ADRs) | One column per `decision`: the question, options with who backs each, the pick, and the quotes behind it, oldest first | 2 or more `decision` items | decision share, plus quotes per decision | Plans whose choices are all made and undiscussed |
| `kanban` | Kanban (Trello, Linear, Jira boards) | One column per state, cards by due date tagged with their group; long columns wrap | 8 or more items, not all in one state | 10 × (1 − share of the largest state) | A plan where nearly everything shares one state |
| `flow` | Phase swimlanes | Groups in lanes, the plan's own phases (`columns`) as columns, arrows for what waits on what | `plan.columns` is set | 8, plus waits-on links | Calendar plans: `timeline` draws dates truthfully |
| `moodboard` | Moodboard (Miro, Pinterest) | Everything at once, each card wearing its evidence; within a group, linked cards in layers (each a row below what it waits on, rows ordered so arrows run short and straight); pinned quotes; gaps and sources | Always | 1 + 10 × share of items with a picture | Plans with little evidence to show |

## Zoom

Every board shares one canvas: drag to pan, Ctrl and scroll or pinch to zoom, Fit to see it all.
Below 50% the canvas is "far", and boards trade detail for a summary readable at that size:
Overview tiles become their group's name and progress, Timeline drops dates under labels, and
Decisions hides its threads. In the far view a click on a summary zooms into it, so a reader goes
from the whole plan to one group to one item page in three clicks.

## Adding a board

1. Write `assets/<id>.js`: `DESIGNS.<id> = { name, hint, build }`, where `build()` returns the scene
   the engine draws (see the comment atop `engine.js`). Add it to `JS` in `build.py`.
2. Add a `Board` to `BOARDS` in `build.py`: when it fits, its score, and the reason it prints.
3. Add a row above, and a test in `scripts/test_build.py` that a plan with the board's data ranks it.
