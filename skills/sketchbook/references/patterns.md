# Pattern catalog

Each pattern is a well-known way to let someone do a job on a kind of data. It is named after the products that made it familiar, so a draft built on it feels learned already.

**Scoring rule.** Score 0 to 10:

1. Start from the share of the core job's records that the pattern places well, times 10.
2. Add 2 if the pattern's main action is the core job.
3. Subtract 3 if it would leave most records in a catch-all ("No date", "Other").

The core job breaks ties. A pattern hit by its "Ruled out by" column scores 0, and that column is the reason given for it.

| Pattern | Known as | Fits when | Main action | Ruled out by |
|---|---|---|---|---|
| Table + record page | Airtable, Notion database, CRM contact list | 20 or more records sharing 3 or more fields | Find, filter, edit, link records | Fewer than 10 records: a list reads faster |
| Master-detail | Mail, Linear's issue list | Records with a lot of detail, handled one at a time | Open one, act on it, next | Records with only a few fields |
| Kanban | Trello, a CRM pipeline | 8 or more records moving through 3 to 7 states | Move a record to its next state | States that don't change, or one state holding most records |
| Inbox / queue | Gmail, Zendesk | Records that arrive and each need one decision | Triage to zero | Records that stay open for long |
| Calendar | Google Calendar month and week views | Events with a start time, several on a day | Find a free slot, see a day | Undated records |
| Resource grid | School timetable, room booking, staff rota | Time slots crossed with resources (rooms, people), repeating weekly | Fill a slot without a clash | One resource only: use Calendar |
| Timeline / Gantt | MS Project, Linear roadmaps | Spans over weeks or months, things waiting on other things | See what is late or blocked | Point events with no spans |
| Agenda / itinerary | TripIt, a printed run sheet | Dated items read in order, often on a phone | See what's next | Items not tied to a date |
| Map + list | Airbnb, Google Maps | Places where distance or area decides | Pick by location | Places that don't matter to the choice |
| Comparison matrix | Wirecutter tables, a spec sheet | 2 to 8 options compared on shared criteria | Choose one | A single option, or criteria that don't line up |
| Checklist | Things, a packing list | Tasks with an owner or a due date, done once | Tick off | Tasks that have more than two states: use Kanban |
| Form wizard | TurboTax, a checkout | Long input, entered once, by someone new to it | Finish it correctly | Input someone repeats daily: use an inline form |
| Dashboard | KPI tiles and charts | Numbers watched over time | Notice a change | Fewer than 3 numbers worth watching |
| Tree / outline | Finder, Workflowy | A hierarchy more than 2 levels deep | Expand, reorder, nest | Flat data |
| Decision log | ADRs, a Notion decision database | Open choices with options and who backs which | Settle a choice | Choices already made |
| Gallery | Pinterest, a moodboard | Visual items browsed for taste | Shortlist by eye | Items without pictures |

## Worked examples

- **Wedding admin board** (app):
  - Data: about 150 guests in parties, split by side, with +1s.
  - Core job: "assign a +1 to a guest".
  - Primary: Table + record page, grouped by party, with a tab per side. The +1 is a guest picker on the record page.
  - Kanban is ruled out. RSVP has only 3 states and moving between them isn't the job.
- **Overseas trip template** (throwaway, no corpus yet):
  - Primary: Agenda / itinerary.
  - Secondary: Map + list for the stay area, and a Checklist for bookings.
- **School timetable** (app):
  - Primary: Resource grid of rooms or teachers by period.
  - Secondary: Table + record page for classes.
- **CRM** (app):
  - Core job: "move a deal forward" makes Kanban the primary.
  - Secondary: Table + record page for contacts.
  - If the core job is instead "log a call", Master-detail is the primary.
