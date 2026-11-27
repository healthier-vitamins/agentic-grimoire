# plan.json and media.json

The contract between the plan folder and the code in `assets/`. `build.py` checks the parts marked **checked** and refuses to build until they hold.

```
<plan-slug>/
  plan.json
  media/media.json      only when the plan has evidence
  media/<files>         photos, screenshots, videos, posters
```

## plan.json

| Field | Meaning |
|---|---|
| `id` | Short slug. Keys the saved card positions. **checked** |
| `title` | The plan's name, as on the title card and the bar. **checked** |
| `glyph` | Optional large watermark character on the title card (`囍`, `上海`). |
| `when` | The display date line (`17 · 07 · 2027`, `1–10 Jan 2027`). **checked** |
| `place` | Optional line under the date. |
| `asOf` | The date the sources were read (`YYYY-MM-DD`). "Today" on every timeline. **checked** |
| `from` | Optional first month of the Flow board and the item timelines. Defaults to `asOf`. |
| `event` | `{ start, end, label?, icon?, note?, group?, col? }`. The event itself: a card in Flow (in the `group` lane), the countdown, the end of every timeline. **checked** |
| `accent` | `{ light, dark }` hex pair. Default jade. |
| `headline` | Optional chips on the title card: `[[icon, text, tone?]]`; tone `warn` paints it red. |
| `source` | Default source line for items that don't name their own. |
| `sources` | `[{ label, url?, read }]`, every source read; shown on the Sources sticky. |
| `states` | Optional subset, in order, of `late now waiting later idea done`. |
| `groups` | `[{ id, name, icon }]` in board order. **checked** |
| `items` | See below. **checked** |
| `dashboard` | `[{ title, icon?, chart, note?, w? }]`: panels across the top of Moodboard and Flow. `w` is the panel's width in pixels (default 330, 380 for votes and swatches, at least 200). **chart type and `w` checked** |
| `agenda` | Optional run-sheet for the day: `[{ phase, place, icon, rows: [{ id, t, end?, what, who?, items?, note? }] }]`. |
| `gaps` | What the sources don't settle yet, one line each. |
| `boards` | Optional board ids in tab order, from [`boards.md`](boards.md). Omitted: `build.py` picks from its ranking. **checked** |
| `columns`, `current` | Optional non-monthly Flow columns: `[[id, label]]` and the id of the column holding today. Each item then names its `col`, and `event.col` places the event card. |

### Items

| Field | Meaning |
|---|---|
| `id`, `title`, `group`, `icon`, `state` | Required. `group` is a `groups` id; `state` one of the six. **checked** |
| `short` | Shorter title for crumbs and link buttons. |
| `due`, `dueLabel` | Due date, or a label when the source gives no date ("Before the trip"). |
| `start`, `end` | A span (a fitting trip, a booking window). |
| `on` | The single event day the item happens on; fills the `days` chart. |
| `slot`, `who`, `cost` | Short facts shown as chips and properties. |
| `notes` | The lede paragraph, from the source. |
| `cover` | A media key: the picture on the card and atop the page. **checked** |
| `media` | More media keys, shown under Evidence on the page. **checked** |
| `link`, `linkLabel` | The item's own page. |
| `source` | Where this item's facts came from. |
| `dependsOn` | Item ids this waits on: arrows on Flow and Moodboard, Waits on / Unlocks on the page. **checked** |
| `onDay` | Agenda row ids this item touches: the page lists those moments. **checked** |
| `quotes` | `[{ who, date, text, pin? }]`, verbatim. `pin: true` also pins it on the Moodboard. **checked** |
| `milestone` | `true` for a date the plan turns on (deposit due, booking opens, the fitting). Needs `due` or `start`. Drawn as a diamond on Timeline and Overview. **checked** |
| `decision` | `{ status, question?, chosen?, options? }` when the item is a choice the group is making. `status` is `open` or `made`; `options` is `[{ name, note?, for?: [who] }]`, and `chosen` names one of them. Drives the Decisions board. **checked** |
| `blocks` | Page sections, below. **type checked** |

Icons are the keys of `ICONS` in `assets/core.js`.

### Blocks

| `type` | Fields |
|---|---|
| `tiles` | `tiles: [[value, label, icon?, tone?]]`: headline facts; tone `warn` for a problem. |
| `callout` | `text, icon?`: one thing the reader must not miss. |
| `iconlist` | `title?, items: [[icon, text, sub?]]` |
| `chipset` | `title, chips: [[icon, text, tone?]]` |
| `people` | `people: [[icon, label]]`: the first is drawn as the lead. |
| `checklist` | `title, items: [text]`: ticks stay in the reader's browser. |
| `gallery` | `media: [key]` **checked** |
| `chart` | `title, icon?, chart, note?` |
| `window` | `from, to, label`: a date window on the plan's timeline ("6–8 weeks before"). |

### Charts

Used by `dashboard` panels and `chart` blocks alike.

| `type` | Fields | For |
|---|---|---|
| `status` | none | Items by state, counted from `items`. |
| `bars` | `rows: [[label, value]], unit?, pick?` | Comparing options: prices by tier, quotes by vendor. `pick` highlights the chosen row. A currency symbol `unit` (`$`, `S$`, `₩`) goes before each number, any other (`KRW`, `of 4 friends`) after it; keep it short and say "per pax" in the panel title. |
| `stack` | `parts: [[label, value]], total?, unit?, rest?, big?` | Parts of one whole: guests by side against the estimate, payments by payer. Up to four parts. |
| `votes` | `options: [{ name, note?, votes: [who], link?, linkLabel? }], pending?: [who]` | A group decision in progress. |
| `swatches` | `colors: [[hex, name]]` | A palette the sources define. |
| `stat` | `value, label, tone?` | One headline number. |
| `timeline` | `points: [[date, label]], span?: [from, to]` | Dated milestones: booking opens, deposit due, the trip. |
| `days` | none | Each day of the event with the items whose `on` falls on it. |

## media/media.json

`[{ key, file, kind, alt, caption?, source, captured?, credit?, license?, licenseUrl?, poster? }]`

| Field | Meaning |
|---|---|
| `key` | What items name in `cover`, `media` and `gallery`. |
| `file` | File name inside `media/`. Must exist. **checked** |
| `kind` | `photo` (from the corpus), `screenshot`, `commons`, `video`. **checked** |
| `alt` | What the picture shows. **checked** |
| `caption` | Optional line under the picture. |
| `source` | `{ label, url? }`: the chat, file or page it came from. `url` required for `screenshot` and `commons`. **checked** |
| `captured` | Date a screenshot was taken. |
| `credit`, `license`, `licenseUrl` | Author and licence; required for `commons`. **checked** |
| `poster` | A still for a video, inside `media/`. |

Photos and screenshots are shrunk and inlined into the page; videos stay as files beside it.
