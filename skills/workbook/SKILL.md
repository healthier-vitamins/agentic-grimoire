---
name: workbook
description: Turn maths questions into one printable revision sheet — the questions first, then worked solutions with every step and a graph drawn by code.
argument-hint: "[questions (PDF, screenshots, list), a test to scope, or a step to explain]"
disable-model-invocation: true
---

Goal: a **workbook** — the questions on their own, then a **worked example** (Sweller & Cooper, 1985) for each one, every move written out. The reader is a **beginner**: a step they cannot follow is a step missing.

## Ground rule: code computes

Every final answer is checked by a SymPy script before it reaches the sheet. Every curve is plotted by pgfplots from the question's own equation, and every marked point is a checked answer. A number, coordinate, or curve shape written from memory is a bug.

## Paths

- **Set** — the user hands over the questions. Run steps 1–6.
- **Scope** — the user names a test. Choose the questions with [`references/scope.md`](references/scope.md), then run steps 1–6 on the list the user confirms.
- **Patch** — the user asks why a step in an existing workbook works. Run [Patch](#patch).

## Steps

1. **Gather.** Read every question with all its parts. Read the official solution wherever the course has one (tutorial solutions, sheet solutions).

   **Done when:** every question has a source tag (`Tutorial 6 Q3(b)`), and every official solution that exists has been read.

2. **Solve and check.** Write one SymPy script in the scratchpad that computes every final answer: derivatives, roots, points, extrema, rates. Compare each against the official solution.

   **Done when:** every final answer matches the script, and every place an official solution disagrees is settled in code and queued as a `Note:` on the sheet.

3. **Write the worked solutions.** In `<sheet-slug>/` under the current working directory, copy [`references/template.tex`](references/template.tex) to `revision.tex`, and write the questions into `body.tex` with each solution inside `\sol{}`. [`references/example.tex`](references/example.tex) is one complete question; match its granularity.
   - `\idea{}` — one line: the method, and why this question calls for it.
   - `\step{}` — one move per step ("differentiate both sides", then "split into one derivative per term"). Each step names its rule or gives its reason. A choice that looks arbitrary — a test value, a substitution, which side to divide — says why it works. A reason that fits in one clause stays in the step ("we can only divide if it is not zero"); a longer one — why a rule has an exception, what happens at an edge case — lives in that rule's `rules.tex` entry, and the step checks the condition in one clause and points there: "n = −2, so the power rule applies (its one exception is on the rules page)".
   - Each `\step{}` title is a command with one action: "Flip both sides."
   - **Rival choice.** Where a step makes a choice (a substitution, a bound, a test value), run one plausible rival through the same steps and show it fail in a small table with a ✓/✗ column. Close with the rule for choosing: "pick u so its slope is already in the integral".
   - **Plain numbers first.** Before a rearrangement on symbols (moving a term, dividing, flipping), do the identical moves on plain numbers and name each stand-in: "12/2 = 6, where 12 plays du and 2 plays dx".
   - `\why{}` — a side note on every line of arithmetic: `(−2x)² = 4x²`, "divide by 3".
   - **Atomic steps.** Every step and every display line does one move, with at most two `=` signs and a 1–4 word `\why{}`. A line that asks the reader to do two moves in their head (differentiate, then put in a number; integrate, then tidy a fraction) becomes two lines or two steps. Write every move the reader would make on paper: a beginner reads any gap between two lines as a missing step.
   - **Mark the change.** Wrap what changed from the line above in `\chg{}`, and strike cancelled factors with `\cancel{}`. Check each cancellation on one plain number: "x = 2: 4 × 1/12 = 1/3 ✓".
   - Checks as steps — dividing by an expression states it is non-zero at the answer; a point found is confirmed on the curve and in the domain.
   - **Continuity.** Each step opens from what the step before it ended with, in the same notation, and says the link in one sentence. Inside a step, each line uses only what the line above produced or what the step named. When a step brings in a new quantity or representation (numbers after symbols, a table after an equation, u after x), it first ties each new item to one the reader already has: which earlier symbol it stands for, how it is worked out from it ("u is worked out from x: feed in x, press e^(−x), take that from 4"), and what each row and column holds.
   - **Integrating in a new letter.** After a substitution, the step that integrates says the `du` only names the letter: `∫ u^(1/2) du` is `∫ x^(1/2) dx` with x renamed u, and the `∫` and `du` leave together once it is done. Then it runs the rule one move per row in a table (add 1 to the power, divide by the new power, tidy the fraction), with the tidy done on plain numbers first.
   - **Answer checks.** A check by differentiating runs as four steps: why it works (integrating undoes differentiating, so the answer's slope equals the integrand); the integrand at the test number; the answer's slope by the chain rule, with outside, inside and multiply each on its own line; then the test number put in, with the match marked ✓.
   - **Test numbers.** Pick a test number where every factor differs from 1 and 0 (x = ln 2, not x = 0, when e^(−x) is a factor), with a small rival table showing what x = 0 would hide. A test value equal to 1 lets a missing factor pass the check.
   - **Why the inside slope.** The first chain-rule step in a sheet says why the inside slope is multiplied in: the outside slope is the change per step of u, and putting u back only renames the letter. Show it with a nudge table: name the start value and the stepped value of x in words ("start at x = 0.6931; add 0.001, so x becomes 0.6941"), then one row per quantity with columns for its value at each x and the change (after minus before). A lone "by how much" column reads as a value at x = 0.001 and a rival row, "outside only, then put u back", that gives the wrong slope.
   - Every claim a step makes is checked on at least one real number.
   - Tables hold results: one number per cell, the working stays in the steps.
   - `\ans{}` — the final result.
   - `rules.tex` — every rule a step uses, each with a one-line example. A rule with a condition (`n ≠ −1`, `x > 0`, a non-zero bottom) says in the same entry what breaks where the condition fails and what to use there instead: "at n = −1 the new power is 0, and you cannot divide by 0; ∫ 1/x dx = ln|x| + C instead".

   **Done when:** every step names a rule or a reason, every rule named appears in `rules.tex`, every condition a rule carries comes with what breaks and what replaces it, and every part of every question ends in `\ans{}`. Every rearrangement has its plain-number run, every cancellation its number check, and every choice its failing rival. Every step and line is atomic and opens from the one before it, with every new quantity or table tied to what the reader already has; every integration in a new letter says what the `du` does and shows each move, every answer check runs as its four steps at a test number with no factor equal to 1, and the first chain rule says why the inside slope is multiplied in.

4. **See it.** End each question's solution with `\seeit{what to look at}{picture}`:
   - Curves from their equations — implicit curves (ellipses, circles) as parametric plots.
   - The template's colours by role for the whole sheet: curve blue, tangent orange, normal purple dashed. Every role also carries a label.
   - Every point the answer names, marked with its coordinates.
   - `axis equal image` wherever angles or shapes carry the meaning (perpendicular lines, circles).
   - Solids and figures (boxes, cones, pentagons) drawn in TikZ from the question's dimensions and labelled with its variables.
   - The caption ties the picture to the answer: "the grey line y = −2x crosses the oval exactly at the two horizontal tangents".

   **Done when:** every question has a picture, and every marked point equals an answer from step 2.

5. **Build and look.** Compile with `tectonic -X compile revision.tex`. If `tectonic` is missing, ask, then install the official release binary into `~/.local/opt/tectonic` with a link in `~/.local/bin` (no sudo). Render every page with `pdftoppm -r 70 -png` and view each image; zoom in (`-r 200`) wherever labels sit close together.

   **Done when:** the build prints no overfull-box warnings, and every page has been viewed with no overlapping labels, no text past the margin, no blank page, and no picture split from its caption.

6. **Hand off.** Name the PDF after the sheet title, inside `<sheet-slug>/`.

   **Done when:** the user has the PDF path, the page count, and every correction made to an official solution.

## Patch

1. Answer in chat, in the sheet's notation, with a small table or ASCII sketch where the idea has a shape.
   - Open with a one-line goal: "The slide wants dx alone on one side."
   - Answer the gap the reader named, then stop. Where the reader says one part landed, keep that part as the anchor and rebuild the rest from it.
   - Where the reader brings their own move, work from it. A valid but unfinished move: say it is correct, run it to the end (plain numbers first, then symbols), and name the one missing step. An invalid move: run it on real numbers until it gives something false, say why, then give the correct route. [`references/patch-examples.md`](references/patch-examples.md) shows both kinds of answer, plus answers to "you skipped a step" and "why multiply by the inside?".
   - Where earlier material overloaded the reader, say what to set aside: "Forget the integral for now."
   - Where the gap is unclear, ask one targeted question. A second attempt takes a new angle.
   - End with a short recipe, one practice problem, and an offer to check their working line by line.
   - Before sending: only what was asked? the reader's own valid method used? every choice has its reason and a failing rival? every sentence 20 words or fewer? every maths word defined with a number?
2. Write the answer where step 3's split puts it: a missing move as new or expanded `\step{}`s at the step that raised it; the reason behind a rule's condition or edge case into that rule's `rules.tex` entry, with the step pointing there in one clause.
3. Search the whole sheet for the same gap — the same unexplained choice in another part, another rule's condition stated without its reason — and fill them too.
4. Rebuild, and view every changed page.

**Done when:** the explanation sits at every step with the same gap, and every changed page has been viewed.

## Style

- **Match the course.** Where a tutorial or sheet PDF from the same course is nearby, render its first page and copy its header lines, paper size and solution colour into the template. Otherwise keep the template as it is.
- **Solution after each question.** The template prints each question (or part), then its blank working space (`\workspace`, 12 cm), then its worked solution straight after, so the reader tries it and checks it at once. The rules page goes at the end of the sheet. Keep that order; never collect the solutions into a separate half.
- **Plain words.** Short sentences. Define each term the first time it appears. Keep the source's own notation (`f′(x)`, `dy/dx`) and spell out every abbreviation.
- **Simplified Technical English.** Sentences of 15 words or fewer, never over 20, one idea each, active voice. One word per meaning: once it is "slope", it stays "slope". Define each maths word with a number example: "the slope of x² at x = 3 is 6". State each step as plain fact; "obviously", "simply", "just" and "clearly" stay off the page.
