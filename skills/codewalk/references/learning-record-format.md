# Learning Record Format

Learning records live in `.codewalk/learning-records/` and use sequential numbering: `0001-slug.md`, `0002-slug.md`, etc. Scan for the highest existing number and increment. Create the directory lazily — only when the first record is written.

They are the teaching equivalent of ADRs: they capture non-obvious insights and demonstrated understanding that steer future sessions. **The records are the learner model** — the zone of proximal development is computed from them each session, never cached elsewhere.

## Template

```md
---
Status: active
Date: {YYYY-MM-DD}
Area: {directory or module, e.g. src/auth}
Fluency: {shaky | solid}
---

# {Short title of what was learned or established}

{1-3 sentences: what was learned (or what prior knowledge was established), and why it matters for future sessions.}

Evidence: {the user's actual answer or statement that demonstrated it}
```

A record can be a single paragraph. The value is recording *that* this is now known and *why* it changes what to teach next.

## The evidence gate

Write a record only when one of these is true:

1. **The user demonstrated genuine understanding of something non-trivial** — evidence they can use the concept, not just that they saw it. Sets a new floor for what to teach next.
2. **The user disclosed prior knowledge** — "I already know the auth flow." Record it, with the depth claimed, so future sessions don't re-teach it.
3. **A misconception was corrected** — the user believed something wrong about the code and now sees why. High value: predicts future stumbling blocks in related areas.

What does **not** qualify:

- Material merely covered in a walk. Coverage is not learning — wait for evidence.
- Codebase facts with no user-understanding component — those belong in `.codewalk/reference/`.
- Session activity logs. Records are decision-grade insights, not a journal.

## Supersession

When a later record contradicts an earlier one (understanding deepened or was corrected), mark the old record `Status: superseded by NNNN` rather than deleting it. How understanding evolved is itself signal for computing the zone of proximal development.
