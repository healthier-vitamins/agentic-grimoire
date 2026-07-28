# Pedagogy

How to question, calibrate, and challenge during a walk. The default goal is **storage strength** (long-term retention), not fluency (in-the-moment recall) — Bjork. Fluency feels like mastery and fades; effortful retrieval is what makes learning stick. Sweep gear trades some of that for coverage, knowingly and only when the user picks it (below).

## Gears — depth or coverage

A **gear** is the whole session's shape, fixed once at SKILL.md Step 3. A **mode** is one area's difficulty inside that gear (below). Say *gear* for the session and *mode* for the area — the two never substitute for each other. (Rejected framing: *pass*. Natural to review ears, but it names no tradeoff, so it anchors no behaviour.)

- **walk** — depth. The 4-6 highest-leverage chunks, question before explanation, aimed at storage strength. The default, and what the rest of this file describes unless a line says otherwise.
- **sweep** — coverage. Every chunk in the target, in reading order, aimed at understanding a diff well enough to review it *today*. Each chunk is one worked example: quote the excerpt, two sentences on what it does and why it is there, then one check the user answers before you move on.

Sweep inverts the ask-first rule deliberately. On unfamiliar material a worked example beats unaided problem-solving (Sweller's worked-example effect), and a check after every small step is what keeps the pace honest (Rosenshine's *Principles of Instruction* — small steps, model it, check for understanding, hold ~80% success). The inversion is scoped to sweep: walk still asks first, because retention is bought with effortful retrieval and coverage does not buy it.

**The check is what makes sweep teaching instead of narration.** One question per chunk, answered, before the next chunk. Keep checks cheap — a one-line prediction, a "which of these two does it do", a "what breaks if this line goes". Sweep buys comprehension you can act on today; walk buys knowing it next month.

## Question rubric

Ask **before** explaining — retrieval builds storage strength, narration does not. (Sweep gear inverts the order, per above; the three types serve both gears.) Three question types:

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

In sweep gear the modes still apply, but they tune the **support level** rather than the ordering: scaffold gets a fuller worked example and a tiny check, socratic gets the terse two-sentence gloss and a real prediction, flaw-hunt swaps the gloss for a mutated copy of the chunk. Downshifting in sweep therefore means more support on the same chunk, never subdividing it — the lesson's chunk list was announced to the user and stays fixed.

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

**Injected bugs live only in chat code blocks — never written to a file (the iron rule in SKILL.md).** Quote the real snippet, present a mutated copy, and say how many bugs it contains.

- **Count:** 1-3 per round.
- **Prefer real over synthetic:** if the walk already surfaced an actual AI mistake, use it — hunting a real bug beats hunting a planted one.
- **Bug taxonomy** (pick to match the code): off-by-one, inverted/weakened condition (`<` vs `<=`, `and` vs `or`), swallowed error (empty catch, dropped return code), wrong-layer call (bypassing an abstraction the codebase enforces), stale/renamed identifier, missing await or unhandled promise, mutation of shared state, boundary not validated.
- **Subtlety ladder:** start with bugs a careful read catches (inverted condition); climb to bugs needing codebase knowledge (wrong-layer call, violated local convention). Climb one rung per successful round.
- Reveal any unfound bug with its explanation — an unexplained miss teaches nothing.

## Anti-patterns

- **No pure narration.** A tour without questions produces recognition, not learning. Orientation gets 60 seconds; everything after is interactive. Quoting the snippet a turn is about is not narration, and neither is sweep's two-sentence gloss — narration is leaving a chunk with the user having answered nothing.
- **No trivia flashcards.** Quiz understanding ("why does this handler re-fetch?"), not facts a grep answers ("what is the function named?").
- **No marathon sessions.** Past ~15 minutes retention drops and the user stops returning. End early with a clean wrap-up rather than pushing through.

## Field notes

`~/.claude/codewalk/field-notes.md` is the skill's own learning record: one line per session, only when a question style or calibration move clearly worked or flopped (e.g. "transfer questions land poorly on first contact with an area — prediction first"). Read it at session start; let it tune question choice. Notes that prove out get folded into this file by hand — the file you are reading is the curated result.
