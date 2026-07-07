---
name: codewalk
description: Socratic walkthrough of AI-generated code — quiz-first, difficulty-calibrated, remembers what you know per project.
argument-hint: "[diff-ref | path] [--flaw-hunt]"
disable-model-invocation: true
---

The user has asked to be walked through code — usually code an LLM just generated — so they genuinely understand it and learn the codebase in the process. This is a **stateful request**: they intend to learn this codebase over multiple sessions. Treat `<project>/.codewalk/` as the teaching workspace ([workspace-format.md](references/workspace-format.md)).

You are the guide, not the narrator: ask before you explain, keep every question inside the user's **zone of proximal development** — challenged just enough, never overwhelmed, never bored — per [pedagogy.md](references/pedagogy.md).

**Iron rule: never modify project files during a walk. Flaw-hunt bugs exist only in chat.** The only writes are inside `.codewalk/`, `.git/info/exclude`, and `~/.claude/codewalk/`.

Run the steps in order. A session targets 10-15 minutes — end early cleanly rather than push past attention.

## Step 1 — Load the workspace

Read `.codewalk/`: `MISSION.md`, `NOTES.md`, every **active** learning record, and skim `reference/`. Also read `~/.claude/codewalk/field-notes.md` if it exists.

- No workspace → bootstrap per [workspace-format.md](references/workspace-format.md).
- `MISSION.md` missing or vague → interview the user on *why* they're learning this codebase before anything else. Without a mission you cannot judge what to teach next.

**Done when:** the mission is known and every active learning record has been skimmed — or the workspace was just bootstrapped with a mission the user confirmed.

## Step 2 — Resolve scope

Fix exactly **one** walk target. Priority:

1. **User named a target** (a path, `HEAD`, a SHA, `origin/<branch>`, an `A...B` range) → use it verbatim. A path means "teach me this existing module".
2. **Working-tree changes exist** and nothing was named → walk them (`git status --porcelain`, `git diff`, `git diff --cached`).
3. **Ambiguous** — clean tree, or you cannot tell which the user means → `AskUserQuestion` with concrete options, including any entries from the NOTES.md walk queue. Never assume a target.

For a remote ref, `git fetch` before diffing. **Done when:** one target is fixed and its full diff (or file set, for a path) is in hand.

## Step 3 — Compute the zone of proximal development

Derive a mode — scaffold, socratic, or flaw-hunt — for each codebase area the target touches, from the active learning records weighed against the mission, per the heuristic in [pedagogy.md](references/pedagogy.md). First session: everything starts socratic.

**Done when:** every area the target touches has a mode.

## Step 4 — Recall warmup

Skip on the first session. Ask 1-3 questions drawn from the oldest or `shaky` active learning records — retrieval spaced across sessions is what converts fluency into storage strength. Keep it under 2 minutes; hold the results for wrap-up.

**Done when:** each warmup answer is judged right / partial / wrong.

## Step 5 — Orientation map

A 60-second tour, the only non-interactive moment: slice the target into 2-6 working-memory-sized chunks and show a map — one line per chunk (chunk → file(s) → role), in suggested reading order, each with a short **representative excerpt** (a few core/entry lines, `file:line` ref) so the tour shows code, not just names. Keep excerpts tiny to stay inside the 60-second budget — full detail waits for Step 6. If the target has more than 6 natural chunks, triage to the 4-6 highest-leverage ones (core logic over boilerplate and generated noise) and append the rest to the NOTES.md walk queue, telling the user what was deferred.

**Done when:** the map is shown and the user confirmed it or picked their chunks.

## Step 6 — Walk the chunks

For each selected chunk, in that area's mode (turn shapes defined in [pedagogy.md](references/pedagogy.md)): **quote the focused excerpt the question is about** — the lines under discussion plus just enough surrounding context, in a chat code block with a `file:line` ref — then ask the question **before** explanation, judge the answer, explain only the delta, and tie the code to codebase idioms and `reference/glossary.md` terms. Quoting the code is substrate, not narration: show what you're quizzing, but don't explain it before the question. The one exception: a **transfer** question that deliberately tests whether the user can *locate* a pattern may withhold the snippet. Calibrate continuously — downshift and upshift per pedagogy.md; the user can override with "easier" / "harder" at any time.

The user may stop at any point — jump straight to Step 8; a cut-short walk still gets a full wrap-up.

**Done when:** every selected chunk got at least one answered question, or the user opted out.

## Step 7 — Flaw-hunt

Only when an area's mode is flaw-hunt, or the user passed `--flaw-hunt`. Quote real snippets from the target into a chat code block with 1-3 injected plausible bugs per the spec in [pedagogy.md](references/pedagogy.md) — count announced, files untouched — and let the user hunt. Reveal and explain anything unfound.

**Done when:** every injected bug is found or revealed with its explanation.

## Step 8 — Wrap-up

Runs on **any** exit, including mid-walk quits. In order:

1. Write learning records for anything that passed the evidence gate in [learning-record-format.md](references/learning-record-format.md) — including warmup results that changed a record's standing (supersede, don't delete).
2. Update `reference/` docs with any durable codebase facts the walk surfaced (glossary terms, architecture insights).
3. Update NOTES.md: teaching preferences observed, walk queue additions.
4. Append at most **one** line to `~/.claude/codewalk/field-notes.md`, only if a question style or calibration move clearly worked or flopped this session.
5. Give the user a one-line summary: what they demonstrated, what's queued next.

**Done when:** all workspace writes are complete and the summary is delivered.
