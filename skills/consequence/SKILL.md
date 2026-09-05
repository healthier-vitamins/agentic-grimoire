---
name: consequence
description: Rewrite a report, spec, or description so every line names what breaks rather than what is. Use when a document gets called convoluted or fluffy, when a reader dismisses a section that actually matters, or before handing written work to someone who has to act on it.
argument-hint: "[path to the draft]"
disable-model-invocation: true
---

# Consequence

**Fluff is not length. Fluff is text that does not change what the reader does.**

That is the whole skill. A terse sentence describing a state is fluff. A longer sentence
naming what breaks is not. Every rule below follows from that one.

Ordinary conciseness advice optimises the wrong variable. It counts words. A document
trimmed three times can still be dismissed whole, because word count was never what was
wrong with it.

## The proof

A technical brief carried a section arguing that a summary route had to learn the identity
of the person asking. The section was already terse — six sentences, 44 words, nothing
decorative:

> The summarise route does not receive the user. The AI Summary service reads the partner
> records again. It then removes fields with a fixed list. That list does not know who
> asks. A Persona Field Set is not possible until you correct this. This section adds no
> function that a user can see.

The reader's verdict: **"this seems useless? what value does this add for this update?"**

They were about to cut a load-bearing security prerequisite. The rewrite was **three times
longer** and reversed them completely:

> Today the summarise route receives a search result, not a user. The service then re-reads
> the partner records itself and strips fields against one fixed list that is the same for
> everybody. So there is no point in the whole system at which the question "who is reading
> this?" can be asked.
>
> That has two consequences, and both matter:
>
> - **The feature is impossible without it.** A Persona that cannot change which fields
>   reach the summary is a Persona that only changes wording.
> - **It is already wrong.** That fixed list is maintained separately from the access rules
>   every other screen enforces. Some readers currently see contact detail in a summary
>   they would be refused on the record itself.

The same reader: **"oh then i have mistaken. keep it. it's extremely necessary. problem is
the wording and description... this description with context is more intuitive to
understand than the original. that's the main issue."**

### What went wrong in the first version

Every sentence was true. Every sentence was short. Four of the six describe the current
state. The fifth carries the consequence — and buries it in an abstract noun, so the reader
has to already know what a Persona Field Set is worth before the stakes exist for them.

The second version is longer and lands, because it answers the only question the reader was
actually asking: **what happens if we don't?**

### The diagnostic

Read a paragraph and ask: **if the reader believed every word of this and still voted to
cut the work, would they be wrong?**

If they would not be wrong, you described. You did not argue. Length has nothing to do with
it.

---

## Part 1 — Drafting

Four rules, in priority order. Rule 4 is last for a reason: sentence polish applied to the
wrong container is wasted work.

### 1. Lead with the consequence, not the state

State-shaped writing describes what is. Consequence-shaped writing names what breaks. The
first is a fact the reader must convert; the second is a decision they can make.

| State-shaped (fails)                          | Consequence-shaped (lands)                                                          |
| --------------------------------------------- | ----------------------------------------------------------------------------------- |
| "The route does not receive the user."        | "There is no point in the system where 'who is reading this?' can be asked."         |
| "Evaluation is manual and Tech-Admin-only."   | "Three personas make ~350 model calls per regression, by hand, every time a file changes." |
| "The mapping is editable at runtime."         | "Without this, correcting a wrong mapping needs a release."                          |
| "Persona definitions are a business decision." | "If this lands late, the plumbing finishes with nothing to put in it."               |

The right-hand column is longer in every row. That is the point.

### 2. Give every section a "why" the reader cannot supply themselves

A section that only lists what to do invites the question "why is this here". Answer it in
the section, before they ask it in a meeting.

The test is whether the reason is derivable. If the reader can work out why the section
exists from its title, do not write it. If they would have to know something you know and
they do not, write it — that is not padding, that is the payload.

### 3. Choose the container the reader already thinks in

The largest single improvement in the source thread was not a word cut. It was moving the
same content from prose into the reader's own working structure.

A 1,634-word narrative was trimmed to 1,390 and still drew "it's still too convoluted."
Rewriting it as an itemised list with stable IDs — the shape the reader would paste into a
tracker — landed at 900 words and ended the objection. Three rounds of prose trimming had
failed at what one structural change fixed.

Later the same content moved again, from numbered sections into epic → ticket → subtask,
because the reader was going to estimate it in Jira. The content barely changed. The
document became usable.

Ask what the reader will do with the document, then give them that shape. A reader who has
to transcribe your structure into theirs will blame your writing.

### 4. Then, and only then, sentence discipline

Once the container is right and each section carries its consequence, tighten the prose.
[ASD-STE100](https://en.wikipedia.org/wiki/Simplified_Technical_English) is a good ruleset
for documents crossing a language or expertise boundary:

- One idea per sentence. Under 25 words.
- Active voice. Present tense.
- One word, one meaning. Do not vary a term for elegance — "summary", "recap" and "digest"
  in one document read as three things.
- Keep the articles. Dropping them saves nothing and costs the reader a parse.
- Name a thing the same way every time, and capitalise defined terms so the reader can see
  which words are load-bearing.

Applied to a document already correct in structure, this pass removed 13% of the words and
nothing else. Applied first, it produces a long draft made of short sentences.

---

## Part 2 — The cut pass

Run over a finished draft, never during one. Conciseness is not achievable on a first pass:
instructing a drafter to be concise yields a long draft with shorter sentences.

### Step 1: Read the whole draft once, without editing

Note where you had to re-read. Those are the candidates, not the long paragraphs.

### Step 2: Run the deletion test on every line

For each line ask, in this order:

1. **Who acts on this?** If no reader makes a different decision because of it, cut.
2. **Does it state a consequence or a state?** If a state, either convert it or cut it. Do
   not shorten it — a shorter description of the same state fails the same way.
3. **Does the reader already know it?** Over-informing is not generosity. It implies they
   might not know, and it costs them the read.
4. **Is this about the work, or about how the work was produced?** Process residue goes.
5. **Do I actually know this?** If not, write the open question as work to be done. An
   honest gap beats confident filler.
6. **Can I name what breaks if I cut it?** If yes, keep it. If no, cut. This is the stop
   rule.

A line that fails is deleted whole, not trimmed.

### Step 3: Look for the four structural cuts

Word-level editing will not find these. They are worth more than the rest of the pass
combined:

- **A column where every row holds the same value.** It is a constant pretending to be
  data. Delete the column and state the constant once.
- **The same fact in two places.** One of them is load-bearing and one is a reminder. Keep
  the one nearer the work.
- **A note dressed as a work item.** If it cannot be assigned, it is not an item. Fold it
  into the item it qualifies.
- **A paragraph that survives as two lines.** Explanatory prose around a list is usually
  the list restated.

### Step 4: Check the container

Re-ask rule 3. If the reader will transcribe this into another shape, you are not finished.

### Step 5: Report the change honestly

Give the before and after word count, and say what you removed and why. If you removed
something the reader may want back, say so rather than hoping they do not notice.

**Done when:** every surviving line answers question 6, no section leaves its reason to be
derived, and the structure matches what the reader will do with it.

---

## Part 3 — The floor

Cutting stops before it takes any of these:

- **The consequence.** The first thing to go in a careless trim and the reason the document exists.
- **The concrete number.** "Roughly 350 model calls per regression" survives; "significant cost" does not.
- **A fact that changes the approach** — a constraint, a dependency, a deprecation.
- **A decision with its owner.** The one provenance that earns its place: a decision can be
  reversed, so someone has to know who to ask.
- **The thing that will surprise them.** If a reader would be angry to learn it late, it
  stays, however inconvenient it is to the shape of the document.

## What always goes

- **Provenance.** How you found out, how many sources agreed, how confident you feel.
- **Hedges and hype.** "Robust", "seamless", "it's worth noting", "may potentially". One
  hedge survives only when it marks a real, load-bearing uncertainty.
- **Glossing.** "In plain words", "essentially", "what this means is". If a sentence needs a
  gloss, rewrite the sentence.
- **Meta-commentary.** Any sentence explaining the document's own machinery.
- **Restatement.** A context sentence that re-says the heading above it.
- **Rejected options.** One earns a line only when someone will otherwise re-propose it.
- **Identifiers, for a non-engineering reader.** File paths, function and class names. Keep
  the product and domain nouns the team says out loud — translating those into euphemism
  costs a decoding step and gains nothing.

## Part 4 — Worked reductions

`references/worked-reductions.md` holds four reductions from a single real thread, with
measured before-and-after and the reader's verdict on each. Read it when a rule above is
clear in principle and unclear in application.

**Criterion:** the rewritten document states a consequence in every section, sits in the
structure its reader will act in, and reports its own before-and-after word count. A reader
who wanted to cut the work can no longer do so without naming what they are giving up.
