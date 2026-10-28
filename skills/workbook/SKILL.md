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
   - `\why{}` — a side note on every line of arithmetic: `(−2x)² = 4x²`, "divide by 3".
   - Checks as steps — dividing by an expression states it is non-zero at the answer; a point found is confirmed on the curve and in the domain.
   - `\ans{}` — the final result.
   - `rules.tex` — every rule a step uses, each with a one-line example. A rule with a condition (`n ≠ −1`, `x > 0`, a non-zero bottom) says in the same entry what breaks where the condition fails and what to use there instead: "at n = −1 the new power is 0, and you cannot divide by 0; ∫ 1/x dx = ln|x| + C instead".

   **Done when:** every step names a rule or a reason, every rule named appears in `rules.tex`, every condition a rule carries comes with what breaks and what replaces it, and every part of every question ends in `\ans{}`.

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
2. Write the answer where step 3's split puts it: a missing move as new or expanded `\step{}`s at the step that raised it; the reason behind a rule's condition or edge case into that rule's `rules.tex` entry, with the step pointing there in one clause.
3. Search the whole sheet for the same gap — the same unexplained choice in another part, another rule's condition stated without its reason — and fill them too.
4. Rebuild, and view every changed page.

**Done when:** the explanation sits at every step with the same gap, and every changed page has been viewed.

## Style

- **Match the course.** Where a tutorial or sheet PDF from the same course is nearby, render its first page and copy its header lines, paper size and solution colour into the template. Otherwise keep the template as it is.
- **Questions first.** The template prints the questions with no answers, each part followed by blank working space (`\workspace`, 12 cm), then the rules page, then the questions again with solutions, so the reader tries each one blind. Keep that order.
- **Plain words.** Short sentences. Define each term the first time it appears. Keep the source's own notation (`f′(x)`, `dy/dx`) and spell out every abbreviation.
