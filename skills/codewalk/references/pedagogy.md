# Pedagogy

How to question, calibrate, and challenge during a walk. The default goal is **storage strength** (long-term retention), not fluency (in-the-moment recall) — Bjork. Fluency feels like mastery and fades; effortful retrieval is what makes learning stick. Sweep gear trades some of that for coverage, knowingly and only when the user picks it (below).

## Gears — depth or coverage

A **gear** is the whole session's shape, fixed once at SKILL.md Step 3. A **mode** is one area's difficulty inside that gear (below). Say *gear* for the session and *mode* for the area — the two never substitute for each other. (Rejected framing: *pass*. Natural to review ears, but it names no tradeoff, so it anchors no behaviour.)

- **walk** — depth. The 4-6 highest-leverage chunks, question before explanation, aimed at storage strength. The default, and what the rest of this file describes unless a line says otherwise.
- **sweep** — coverage. An annotated read-through: every chunk in the target, in reading order, snippet quoted, terse gloss, **zero questions** — aimed at understanding a diff or module well enough to act on it *today*.

Sweep drops retrieval deliberately and runs on the playbook for non-interactive instruction — not on walk-minus-questions. On unfamiliar material a worked example beats unaided problem-solving (Sweller's worked-example effect), so each chunk is one worked example: snippet first, then gloss. Everything else is structure doing the teaching that questions do in walk (Mayer's multimedia principles):

- **Segmenting** — learner-paced parts beat a continuous stream: at most 8 chunks per part (Miller's working-memory limit); the user says "next" between parts. That "next" is pacing, never a quiz.
- **Coherence** — extraneous material hurts learning: the gloss is 2-4 sentences — what it does, why it is there, what it connects to — nothing decorative, nothing convoluted.
- **Signaling** — structural cues (the orientation map, numbered reading order, part map) carry the reader through the material.

The tradeoff stays stated: sweep buys comprehension you can act on today; walk buys knowing it next month.

## Question rubric

Walk gear only — sweep asks nothing. Ask **before** explaining — retrieval builds storage strength, narration does not. Three question types:

- **Prediction** — "What does this function return when `items` is empty?" Use to test whether the user can execute the code mentally. Best for logic, control flow, edge cases.
- **Explanation** — "Why did the AI route this through the repository layer instead of calling the ORM directly?" Use to test design understanding. Best for architecture, patterns, tradeoffs.
- **Transfer** — "Where else in this codebase does this pattern appear?" Use to connect new code to existing knowledge. Best for idioms, conventions, cross-cutting concerns.

**Show the code you're quizzing.** Quote the focused excerpt alongside the question — the lines the question targets plus minimal surrounding context, in a chat code block with a `file:line` ref — so the user reads the code in place instead of hunting for it. This is substrate, not narration (see anti-patterns): showing the snippet ≠ explaining it. The flaw-hunt spec below already works this way. Exception: a transfer question that tests whether the user can *locate* a pattern may withhold it.

Judge each answer right / partial / wrong, then explain only the **delta** — the gap between their answer and the full picture. Never re-explain what they already demonstrated.

Quiz hygiene: when offering multiple-choice options, keep every option the same length and register — formatting must not leak the answer.

## The three modes

Each codebase area sits in one mode. A mode describes what one turn looks like:

- **scaffold** — worked example first: walk one small piece line by line, *then* ask a tiny prediction about the very next piece. High support, small chunks. For areas the user has no footing in.
- **socratic** — question first, always. Prediction or explanation question on the chunk, judge, explain the delta. The default mode.
- **flaw-hunt** — challenge mode. Quote real code with injected bugs and let the user hunt (spec below). For areas the user has demonstrated solid understanding of.

Modes are walk gear's dial. Sweep ignores them — the only record-driven adjustment is terseness: an area recorded `solid` gets a shorter gloss.

## Computing the zone of proximal development

Derive each area's mode from the learning records at session start — do not cache the result:

1. List the codebase areas the target diff touches (by directory/module).
2. For each area, scan **active** learning records mentioning it:
   - No records → **scaffold** if the area is dense/novel, else **socratic**. First session: everything starts socratic; calibrate live.
   - Records with `shaky` fluency, or a corrected-misconception record → **socratic**, aimed at the recorded weak spot.
   - ≥2 records with `solid` fluency and no recent misconceptions → **flaw-hunt** eligible.
3. Weigh against MISSION.md: areas central to the mission deserve stretch (one mode harder); peripheral areas get the comfortable mode.

## Calibration during the walk

Difficulty is per-area, never global — an expert in the API layer can be a novice in the build system (expertise reversal: scaffolding that helps a novice actively hurts an expert, and vice versa).

- **Downshift** (one mode easier, smaller chunks) when: ~2 wrong answers in a row, visibly guessing, or the user signals overwhelm ("no idea", long hedging). Never push a struggle the user lacks footing for — past the zone, difficulty stops teaching and starts repelling.
- **Upshift** (one mode harder, subtler questions) when: consecutive fast, correct, confident answers. Boredom wastes the session as surely as overwhelm.
- The user can always override: "easier" / "harder" / "just explain this one".

## Flaw-hunt spec

Walk gear only. **Injected bugs live only in chat code blocks — never written to a file (the iron rule in SKILL.md).** Quote the real snippet, present a mutated copy, and say how many bugs it contains.

- **Count:** 1-3 per round.
- **Prefer real over synthetic:** if the walk already surfaced an actual AI mistake, use it — hunting a real bug beats hunting a planted one.
- **Bug taxonomy** (pick to match the code): off-by-one, inverted/weakened condition (`<` vs `<=`, `and` vs `or`), swallowed error (empty catch, dropped return code), wrong-layer call (bypassing an abstraction the codebase enforces), stale/renamed identifier, missing await or unhandled promise, mutation of shared state, boundary not validated.
- **Subtlety ladder:** start with bugs a careful read catches (inverted condition); climb to bugs needing codebase knowledge (wrong-layer call, violated local convention). Climb one rung per successful round.
- Reveal any unfound bug with its explanation — an unexplained miss teaches nothing.

## Anti-patterns

- **In walk, no pure narration; in sweep, no wall of text.** A walk without questions produces recognition, not learning — orientation gets 60 seconds, everything after ends with the user answering; narration is leaving a chunk with the user having answered nothing. Sweep teaches through structure instead, and an unsegmented, unsignaled dump defeats it as surely as a quizless walk — parts of ≤8 chunks, glosses of ≤4 sentences, map first.
- **No trivia flashcards.** Quiz understanding ("why does this handler re-fetch?"), not facts a grep answers ("what is the function named?").
- **No marathon sessions.** Past ~15 minutes retention drops and the user stops returning. End early with a clean wrap-up rather than pushing through.

## Field notes

`~/.claude/codewalk/field-notes.md` is the skill's own learning record: one line per session, only when a question style or calibration move clearly worked or flopped (e.g. "transfer questions land poorly on first contact with an area — prediction first"). Read it at session start; let it tune question choice. Notes that prove out get folded into this file by hand — the file you are reading is the curated result.
