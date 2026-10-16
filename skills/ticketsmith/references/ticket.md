# The ticket

One parent ticket explains the work as a whole. The work breaks into **items**: one table row
per item on the parent, and one sub-task per item under it. Status lives in each ticket's own
status field.

## Parent ticket

```
# <title: the work, in a few words>

<Explanation, at most 3 sentences: what the work is and why, who raised it or what it
answers, and where it stands (built, shipped, waiting).>

### <table heading: names the source, e.g. "Review comments and the changes made">

| # | <area> | <ask> | <change> |
| - | ------ | ----- | -------- |
| 1 | <where in the product> | - <point> | - <point> |

### Also <done | covered>
- <related work folded into this ticket: one point per area>
```

- **Columns.** Name them from the source. A review list gives *Guide section / Comment /
  Change made*. Work with no source gives *Area / What / Change / Status*.
- **Ask cell.** The reviewer's point, with any wording they suggested kept in quotes.
- **Change cell.** What the product or document does now. For an item still open, the next
  step.
- **Also section.** Only when the user folded related work into this ticket. Each point names
  the area first ("Feature Request board: ...").

## Sub-task

One per table row, plus one per area in the *Also* section.

```
<title: verb + object, e.g. "Reword the division access example">

- <point: what was wrong or asked>
- <point: what it is now>
```

- One to three points.
- The points match the table row; they never add facts the table lacks.

## Fields

Ask in the interview, and print in the preview: issue type, parent (epic), label, sprint,
assignee, status, original estimate. Leave a field out when the user gives no value for it.
