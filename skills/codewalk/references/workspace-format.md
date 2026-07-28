# Teaching Workspace Format

`<project>/.codewalk/` is the teaching workspace. All learning state for this codebase lives here:

```
.codewalk/
├── MISSION.md            # why the user is learning this codebase
├── NOTES.md              # teaching preferences + walk queue
├── learning-records/     # the learner model — see learning-record-format.md
└── reference/            # durable compressed codebase knowledge
```

## Bootstrap (first session)

1. `mkdir -p .codewalk`
2. Keep it out of git without touching the shared `.gitignore` — the learner's knowledge gaps are private:
   ```bash
   grep -qxF '.codewalk/' .git/info/exclude 2>/dev/null || echo '.codewalk/' >> .git/info/exclude
   ```
   (Not a git repo → skip; nothing to exclude from.)
3. Interview the user for the mission, then write `MISSION.md`.
4. `learning-records/` and `reference/` are created lazily on first write.

## MISSION.md

Captures the *reason* the user is learning this codebase. Every teaching decision — which chunks to walk, how hard to push an area — traces back to it.

```md
# Mission: {codebase / project name}

## Why
{1-3 sentences. The concrete outcome: "own the payments module so I can review AI changes to it unaided", not "understand the code".}

## Success looks like
- {A specific, observable ability, e.g. "can predict what a diff to src/billing does before reading the explanation"}

## Out of scope
- {Areas the user explicitly doesn't care about — protects the zone of proximal development}
```

Rules: one mission per workspace; concrete over abstract; push back on vagueness — interview before writing, a bad mission is worse than none; revise when the goal shifts (confirm with the user, and write a learning record capturing the shift); keep it under a screen.

## NOTES.md

Scratchpad with two sections:

```md
# Notes

## Preferences
- {How the user likes to be taught: usual gear, pace, question style, session length…}

## Walk queue
- {chunk or area} — {source diff/ref} — {one-line why it was deferred}
```

The walk queue holds chunks triaged out of oversized diffs; offer them as targets at the next session's scope step.

## reference/

Durable codebase knowledge worth revisiting — walks are ephemeral, references are not. One file per topic, e.g.:

- `glossary.md` — the codebase's own nomenclature (domain terms, internal names). Once a term is defined here, use it consistently in every walk.
- `architecture.md` — module map, layering rules, data flow cheat-sheet.

Keep entries compressed — quick-reference format, not prose. Update them whenever a walk surfaces a durable fact; they double as material for warmup questions.
