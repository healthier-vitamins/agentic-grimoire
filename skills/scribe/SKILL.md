---
name: scribe
description: Write the way I write, for one reader, in the voice of my samples.
argument-hint: "[what to write, or a draft to cut]"
disable-model-invocation: true
---

# Scribe

**Write for one reader.** A model defaults to a reader who could be anyone, so it explains
what the real reader already knows: the timezone, how a table works, why a date shows up
twice. Name the actual reader first (the teammate on the ticket, the manager skimming the
summary, the examiner marking the answer) and leave out whatever they already share with the
writer.

## Match the sample

Before drafting, read whichever file in `samples/` fits the medium, plus any sample the user
passes in. Match its line length, punctuation, labels, openings and sign-offs. A sample
outranks every rule below.

Two habits from the samples are worth reaching for when they suit the reader. An update
says who was told and what happens next. A table doubles as the work surface when items get
worked through one by one, with a status per row (`[FIXED]`, `[ALREADY ALIGNED]`). Choose a
different form whenever the medium, the reader or their level calls for one.

`samples/` is local only and never committed. If it is missing or nothing in it fits, work
from the rules below.

## Rules

### 1. Mechanism over concept

State who does what to whom.

Rejected. *Google's dominance shapes competition less by winning on quality than by
controlling where search begins.*

Accepted. *Google pays Apple, Samsung and browser makers to make Google the default search
engine. Most users never change the default.*

### 2. Context before parts

Name the system before its components.

Rejected. *Google owns the publisher's ad server, the exchange the auction runs on, and the
tool advertisers bid with.*

Accepted. *An advertisement space on a web page is sold in an automatic auction, and three
programs run that sale.* Then the three.

### 3. Length is borrowed, not chosen

Match the length of prose already present in the same document. Where there is none, take the
number from the brief. "Concise" on its own decides nothing.

Rejected. 200-word answers beside the user's own answers of 67 and 106 words.

Accepted. 110 words in the same shape as theirs, claim first, elaboration second.

### 4. Answer the question asked

Cut any paragraph arguing an adjacent question, however well it argues it.

Rejected, in an answer asking what a breakup *would do*. *A breakup is also not needed to fix
the problem.* That argues which remedy is better.

Accepted. *It would speed up everyone else.* That is an effect.

### 5. Inference shows its basis

An inference drawn from a brief states its basis in the brief's own wording.

Rejected. *Cutting a route drives riders away.*

Accepted. *The second goal puts more buses where passengers are packed in at peak. The fleet
is fixed, so those buses come from quieter routes.*

### 6. Sourcing

Primary sources only: court filings, SEC filings, a company's own statement, the brief itself.
Print only figures visible in a document actually read, and say plainly what could not be
confirmed.

### 7. Polished prose

In essays and set answers, vary sentence length, break with a comma or full stop where a dash
would go, and carry transitions in words ("This is mitigated by...") rather than label colons.
Working notes between colleagues follow the sample instead, labels and parallel lists included.

## Answering a set question

- The question is the heading, word for word, including its spelling and point values.
- Exhaust the data the brief supplies before assuming any.
- An assumption is declared once in the open, or it is dropped.
- Check the referent of every ambiguous noun in the brief before building on it.
  "Overcrowding" meant passengers, not vehicles.

## Cleanup pass

After drafting, read [`references/ai-tells.md`](references/ai-tells.md) and edit the draft
against it. Act on §1 to §5 at one sighting and on a *weak alone* pattern only when others
share its passage. Where the sample does something the file lists as a tell, keep the sample's
habit.

## Done when

- The reader is named, and nothing in the text explains what that reader already shares.
- The draft matches the sample's line length and punctuation, or rules 1 to 7 where no sample fits.
- Every figure traces to a document actually opened (rule 6).
- Every pattern in `references/ai-tells.md` has been checked, and each one left in is deliberate.
