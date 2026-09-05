# Worked reductions

Four reductions from one real thread: an engineer writing a technical specification for a
non-technical audience, revised across four versions under direct reader feedback. Word
counts are measured, not estimated. Reader verdicts are quoted verbatim.

The fifth and most important reduction — a section that got **three times longer** and
succeeded — is in `SKILL.md` under "The proof". Read that one first.

---

## R1 — The container change

**1,634 words → 1,390 words → still rejected → 900 words and accepted.**

The first draft was a narrative brief with ten prose headings. It was 1,634 words against a
self-imposed budget of "one page, two at most".

**Round 1, self-caught.** Trimmed to 1,390 words. Sentences shortened, hedges removed,
two headings merged. Honest reduction, 15% off.

**Reader verdict:** _"it's still to oconvluted. i need a list of actionable items. rmemeber
dont need to go into details. just briefly explain what needs to be done so i can do story
esimation and time estimation and jira ticket updating."_

**Round 2, structural.** The prose was thrown away. Same content became 19 engineering items
and 4 business items, each one line, each with a stable ID (`P1-1`, `B3`), grouped by phase,
with a blocking-dependency column. 900 words. Accepted immediately.

### What this teaches

Three rounds of prose trimming had failed at what one structural change fixed. The problem
was never word count — 1,390 words of prose was less usable than 900 words of list because
the reader's next action was to create tickets, and prose does not decompose into tickets.

The reader named their own next action in the rejection: _story estimation, time estimation,
Jira ticket updating._ That sentence was the specification for the container. It was
available before the first draft and went unused.

**Rule:** ask what the reader will do with the document before choosing its shape. When they
tell you, that is not context — it is the requirement.

---

## R2 — The sentence pass

**1,290 words → 1,121 words. 23 items → 21. No content lost.**

Applied to a document whose structure was already correct. Two things ran together: an
[ASD-STE100](https://en.wikipedia.org/wiki/Simplified_Technical_English) rewrite (one idea
per sentence, active voice, present tense, one word one meaning) and four structural cuts.

The sentence rewriting produced most of the readability. **The four structural cuts produced
most of the word reduction**, and no amount of sentence-level editing would have found them:

| Cut                        | What it was                                                                            | Why it went                                              |
| -------------------------- | -------------------------------------------------------------------------------------- | -------------------------------------------------------- |
| **Constant as a column**   | An "Owner" column where all five rows said "Product"                                   | A constant pretending to be data. Stated once in prose.  |
| **The duplicate**          | Item 2d ("communications plan") repeated item 1e                                        | Kept the one nearer the work it describes.               |
| **The note dressed as work** | Item 7c: "same permission as 5b" — a qualifier, not an assignable task                | Folded into 7b, which is the assignable item.            |
| **Prose around a list**    | A four-sentence paragraph explaining a storage decision above the list that showed it  | Two lines. The list already said it.                     |

A "Reuse or new" column also went: with a size estimate already on every row, it changed
nobody's decision.

### What this teaches

Run the structural pass before the sentence pass, and expect it to be worth more. Sentence
editing is visible work that feels productive; deleting a column is invisible work that
returns more.

**Rule:** in any table, check whether a column has one distinct value. If it does, it is a
sentence, not a column.

---

## R3 — Growing a document on purpose

**1,121 words → 1,446 words. 29% longer. Better.**

The reader's instruction was to emphasise that a step needed real technical planning, even
though the implementation was small. The section had been five one-line items. It became:

> **The build here is small. The design is not.**
>
> The build is one markdown file for each Persona. The prompt loader already reads a file by
> name, so a new Persona is a new file name. That is the whole mechanism.
>
> The design decides whether that mechanism holds after the third file, and every answer
> below is expensive to reverse once three files exist. [five named questions follow]

Plus one new work item: a design ticket, sized and gating the rest of the section.

### What this teaches

Every added word was consequence. "Expensive to reverse once three files exist" is the
sentence that justifies a design ticket to someone who can see the implementation is
trivial. Without it, a reader looks at a one-line change and asks why it needs a spike —
and they are right to ask, because nothing in the document answered them.

This is R1's lesson pointed the other way. The 1,634-word draft was too long because its
words were description. This document got longer and improved because its words were stakes.

**Rule:** never accept a word-count target as the goal. Length is an output, not a
constraint. The constraint is whether a reader can act.

---

## R4 — Moving into the reader's tracker

**Same content. New container. Nine sections → one epic, nine tickets, subtasks under each.**

The reader described how they wanted it: _"this entire thing will be an epic. then each
ticket the relevant substasks."_ They sketched four example tickets and added _"they're just
examples. if they're relevant then good. if not im not attached to any of those."_

The rewrite kept the sketch's spirit and reorganised the work: two of the sketched tickets
merged, because folder structure is the output of the design note rather than a separate
task, and role resolution belongs with the resolver rather than alone.

Every ticket then gained a **Why** paragraph, written as consequence — the change that came
directly from the reader's own feedback about the failed section.

### What this teaches

Two distinct moves, and both were needed:

1. **The container** came from the reader. They named epic, ticket and subtask, so those are
   the headings. Do not improve on a container the reader named.
2. **The content within it** was reorganised on engineering judgement, because the reader
   explicitly released it: _"they're just examples."_ Copying a sketch faithfully when the
   author has told you it is illustrative is not deference, it is abdication.

**Rule:** take the structure from the reader and the grouping from the domain. When they
conflict, the reader's structure wins and the grouping bends inside it.

---

## The sequence

The four reductions run in a fixed order, and doing them out of order wastes the earlier
work:

1. **Container** (R1, R4) — what shape does the reader act in?
2. **Consequence** (R3, and the proof in `SKILL.md`) — does each section say what breaks?
3. **Structural cuts** (R2) — constants as columns, duplicates, notes dressed as work,
   prose restating a list.
4. **Sentences** (R2) — one idea, active, present, consistent terms.

A sentence pass over the wrong container is polish on a document that will be rewritten.
