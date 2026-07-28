# House style

The standard for the drafted ticket: a teammate reads it in under a minute and knows what
to do. These rules govern the ticket output only, not this doc.

The skill runs Socrates twice. `grill-me` is **maieutics** — questioning that delivers what
the user already knows. The cut (Step 6) is **elenchus** — cross-examining the draft's own
claims until each one survives or collapses. Drafting adds; only the cut subtracts.

## 1. The genre rule

**A ticket is not a research report.** A report answers *what did we learn and how do we
know it's true*. A ticket answers *what is wrong, what we will try, how we will know*.
Every sentence serving the first question is cut.

This is the failure mode when the seed is research. The ticket is the research's
**residue**, not its summary: the findings stay in the research doc, and only what changes
what we do next crosses over. Reformatting a report into ticket headings is the mistake —
the report's own scaffolding (options tables, provenance columns, grounding citations)
travels with it and buries the ask.

**The template is the whole ticket.** Do not invent sections. If the material will not fit
under *User story* and *Acceptance criteria*, it belongs in the research doc.

## 2. The elenchus

Interrogate every line with the same six questions. A line that cannot answer is deleted
whole, not trimmed.

1. **Who acts on this?** If no reader makes a different decision because of it, cut.
   (Grice's maxim of relation.)
2. **Does the reader already know it?** Over-informing is not generosity; it implies the
   reader might not know, and it costs them the read. (Grice's maxim of quantity.)
3. **Is this about the work, or about how the work was produced?** Process residue is cut —
   see §3.
4. **Can it be said in half the words?** Then say it in half. "Omit needless words"
   (Strunk & White, Rule 17); "if it is possible to cut a word out, always cut it out"
   (Orwell, *Politics and the English Language*).
5. **Do I actually know this?** If not, write the open question as work to be done. Honest
   *aporia* beats confident filler. (Grice's maxim of quality.)
6. **Can I name what breaks if I cut it?** If yes, keep it. If no, cut. This is the stop
   rule — Chesterton's fence, run in reverse.

## 3. What always goes

- **Provenance.** Which pass proposed an idea, how many sources agreed, how confident the
  writer feels. The reader wants the idea, not its pedigree.
- **Grounding citations.** A citation defends the writer; it does not tell the assignee what
  to build. Keep them in the research doc.
- **Rejected options.** A rejected option earns a line only when someone will otherwise
  re-propose it. Eight ruled-out rows collapse to zero.
- **Glossing.** "In plain words", "essentially", "what this means is". If the sentence needs
  a gloss, rewrite the sentence.
- **Meta-commentary.** Any sentence explaining the document's own machinery ("the From
  column shows...") is scaffolding left standing after the build.
- **Restatement.** A context sentence that re-says the title or the story adds nothing.
- **Hedges and hype.** "Robust", "seamless", "it's worth noting", "may potentially". One
  hedge survives only when it marks a real, load-bearing uncertainty.
- **Emdashes.** Use full stops, commas, or parentheses. Emdashes read as AI boilerplate.

## 4. What always stays

The floor. Cutting stops before it takes any of these:

- **The symptom** — what is wrong, concretely, ideally with the input that reproduces it.
- **The ask** — what we will try.
- **The done-check** — how we will know.
- **A fact that changes the approach** — a deprecation, a constraint, a dependency.
- **A decision, with its owner and date.** This is the one provenance that earns its place.
  A finding needs no source; a decision does, because it can be reversed and someone has to
  know who to ask. "As of 28/07, Zoe clarified names shouldn't be searchable."

## 5. Speak the team's language

Write to a peer, not to a stranger. **Identifier-free means codebase-free, not
domain-free:**

- **Cut** file paths, function, class, and module names, framework internals. These are
  meaningless outside the repo and rot on the next rename.
- **Keep** the product, vendor, and domain nouns the team says out loud in standup — the
  search service by name, the re-ranking step, the evaluation module. Translating these
  into euphemism ("the search engine vendor") costs the reader a decoding step and gains
  nothing. Orwell's rule against jargon targets words that obscure; a team's shared
  technical noun *is* the everyday equivalent for that audience.

Lead with the answer, then support it (Minto's pyramid). The reader who stops after the
first line should still have the point.

## 6. Subtraction is a second pass

> "I have made this longer than usual because I have not had time to make it shorter."
> — Pascal

Conciseness is not achievable on a first draft, by a person or a model. Instructing a
drafter to *be concise* produces a long draft with shorter sentences. This is why the cut
is a separate step over a finished draft: draft for completeness, then subtract.

The direction is always **via negativa** — remove rather than rewrite. "Perfection is
attained not when there is nothing more to add, but when there is nothing left to take
away" (Saint-Exupéry). What the writer knowingly omits still strengthens the piece; the
research was real and stays under the waterline (Hemingway's iceberg).

## 7. Worked reduction

One row, across three drafts. Same idea each time.

**Draft 1** — research report in ticket clothing:

> Write down a list of test questions with known right answers (including questions that
> must return nothing) and measure today's search against it before changing anything. Fix
> the benchmark loophole where a question with no expected answer passes no matter what junk
> comes back.
> *From:* both. *Grounded in:* LinkedIn measures precision, recall and ranking separately
> across stratified query categories rather than as one blended score (LinkedIn search stack)

**Draft 2** — compressed, same genre:

> Write test questions with known answers, including ones that must return nothing, and
> baseline today's search first. Fix the loophole where a no-expected-answer question passes
> on any junk. — LinkedIn

**Draft 3** — the ticket:

> Add new test cases and queries in evaluation module

Draft 2 halves the words but keeps the genre: it still carries provenance ("both") and
grounding ("LinkedIn"), so it still reads as a defence of an idea rather than an
instruction. Draft 3 changes genre. The grounding goes (§3), the provenance goes (§3), and
the rationale goes because the reader is the person who will write the tests and already
knows why tests exist (question 2).

Draft 3 sits at the floor, which is where the last increment of cutting gets decided:
the loophole detail comes out only if the assignee cannot act wrongly without it
(question 6). Judge that per ticket rather than cutting on reflex.

The largest single cut in the same reduction was structural: an eight-row *Blocked or ruled
out* table went to nothing, and a three-paragraph preamble explaining the document's own
columns went with it. Neither survived question 1 — no reader acts on either.
