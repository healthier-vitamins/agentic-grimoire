---
name: codewalk
description: Socratic walkthrough of AI-generated code — quiz-first walk or a granular read-only trace, difficulty-calibrated, remembers what you know per project.
argument-hint: "[diff-ref | path] [--walk | --sweep] [--flaw-hunt]"
disable-model-invocation: true
---

The user has asked to be walked through code — usually code an LLM just generated — so they genuinely understand it and learn the codebase in the process. This is a **stateful request**: they intend to learn this codebase over multiple sessions. Treat `<project>/.codewalk/` as the teaching workspace ([workspace-format.md](references/workspace-format.md)).

In walk gear you are the guide, not the narrator: every chunk ends with the user answering something, and every question stays inside their **zone of proximal development** (Vygotsky) — challenged just enough, never overwhelmed, never bored. In sweep gear you are the tracer: the target broken into atomic steps, each excerpt quoted under its own why-line, zero comprehension questions — structure does the teaching. Both per [pedagogy.md](references/pedagogy.md).

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

For a remote ref, `git fetch` before diffing. **Size gate:** an unbounded target — the whole repo, a root path — is too big to teach well in a session. Kindly decline and offer 2-4 concrete flows or modules from it as targets instead. A bounded target holding several flows is in scope: walk triages it at Step 6, sweep gates it into chains.

**Done when:** one target is fixed, it passes the size gate, and its full diff (or file set, for a path) is in hand.

## Step 3 — Pick the gear

One gear for the whole session — depth or coverage, defined in [pedagogy.md](references/pedagogy.md). Difficulty still calibrates per area inside it (Step 4).

- `--walk` or `--sweep` passed → use it, no question.
- Otherwise → `AskUserQuestion`, one question, recommending the gear NOTES.md records as this user's usual and `walk` when it records none: **walk** (depth — the highest-leverage chunks, quizzed before explained, built for remembering this next month) or **sweep** (coverage — the target decomposed into atomic steps, each excerpt quoted with its why, zero comprehension questions, built for consuming a diff or module today).

**Done when:** the session's gear is fixed and named back to the user in one line.

## Step 4 — Compute the zone of proximal development

Walk gear only — sweep goes straight to Step 6 (learning records only shorten steps on `solid` areas, per [pedagogy.md](references/pedagogy.md)). Derive a mode — scaffold, socratic, or flaw-hunt — for each codebase area the target touches, from the active learning records weighed against the mission, per the heuristic in pedagogy.md. First session: everything starts socratic.

**Done when:** every area the target touches has a mode.

## Step 5 — Recall warmup

Skip on the first session and in sweep gear. Ask 1-3 questions drawn from the oldest or `shaky` active learning records — retrieval spaced across sessions is what converts fluency into storage strength. Keep it under 2 minutes; hold the results for wrap-up.

**Done when:** each warmup answer is judged right / partial / wrong.

## Step 6 — Orientation map

A 60-second tour (Ausubel's advance organizer — orient before detail). **Walk:** slice the target into working-memory-sized chunks and show a map — one line per chunk (chunk → file(s) → role), in suggested reading order, each with a short **representative excerpt** (a few core/entry lines, `file:line` ref) so the tour shows code, not just names. Keep excerpts tiny to stay inside the 60-second budget — full detail waits for Step 7. **Sweep:** the chain map is the organizer.

The map and any oversize are handled by the gear:

- **walk** — more than 6 chunks → triage to the 4-6 highest-leverage ones (core logic over boilerplate and generated noise) and append the rest to the NOTES.md walk queue, telling the user what was deferred.
- **sweep** — detect the chains and run the chain gate ([trace-format.md](references/trace-format.md)): one chain proceeds; two or more stop, show the chain map, and ask which the user wants first, every chain written to `.codewalk/sweep/chains/` before the question. Inside the chosen chain, more than 8 steps → number them into **parts** of at most 8 (working-memory limit), show the part map up front, deliver part 1, and continue when the user says "next" — same session, learner-paced (Mayer's segmenting principle, per [pedagogy.md](references/pedagogy.md)). "Next" is pacing, never a quiz. Coverage is kept by segmenting, never by dropping.

**Done when:** the map is shown — walk: the user confirmed it or picked their chunks; sweep: one chain is fixed (the only chain, or the user's pick) and every detected chain has a file.

## Step 7 — Walk the chunks

Work the chunks in the session's gear — turn shapes in [pedagogy.md](references/pedagogy.md). Both gears **quote the focused excerpt** the turn is about (chat code block, `file:line` ref) and tie the code to codebase idioms and `reference/glossary.md` terms.

- **walk** — each chunk in its area's mode: ask, judge the answer, explain only the delta. Calibrate continuously — downshift and upshift per pedagogy.md; the user can override with "easier" / "harder" at any time.
- **sweep** — each step in the shape and granularity of [trace-format.md](references/trace-format.md): header, excerpt, why-line, one-idea bullets, one connective line to the previous step or a codebase idiom. Zero comprehension questions; next step.

The user may stop at any point — jump straight to Step 9; a cut-short session still gets a full wrap-up.

**Done when:** walk — every selected chunk got at least one answered question; sweep — every step of every part in the chosen chain delivered; or the user opted out.

## Step 8 — Flaw-hunt

Walk gear only — when an area's mode is flaw-hunt, or the user passed `--flaw-hunt`. Quote real snippets from the target into a chat code block with 1-3 injected plausible bugs per the spec in [pedagogy.md](references/pedagogy.md) — count announced, files untouched — and let the user hunt. Reveal and explain anything unfound.

**Done when:** every injected bug is found or revealed with its explanation.

## Step 9 — Wrap-up

Runs on **any** exit, including mid-walk quits. In order:

1. **Walk:** write learning records for anything that passed the evidence gate in [learning-record-format.md](references/learning-record-format.md) — including warmup results that changed a record's standing (supersede, don't delete). **Sweep:** no learning records — no answers means no fluency evidence. Flip the traced chain's file to `Status: traced` and append one "covered" line to NOTES.md (target, date, chain, parts delivered): exposure, not fluency.
2. Update `reference/` docs with any durable codebase facts the walk surfaced (glossary terms, architecture insights).
3. Update NOTES.md: teaching preferences observed — including the gear, once the user's choice is settling into a habit — and walk queue additions.
4. Append at most **one** line to `~/.claude/codewalk/field-notes.md`, only if a question style or calibration move clearly worked or flopped this session.
5. Give the user a one-line summary: what they demonstrated, what's queued next.

**Done when:** all workspace writes are complete and the summary is delivered.
