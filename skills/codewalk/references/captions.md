# Captions

Write every walkthrough step for a reader who is new to this code, and maybe new to the
language. They have not read the files, the design notes, or earlier versions. They read the
steps in order, and they must not need to leave the page to understand one.

## Shape of one step

- `title` — at most 6 words. It names what this code does: "The route checks the request".
  The rail lists the titles, so a reader finds a step by its title.
- `caption` — three or four paragraphs, with a blank line (`\n\n`) between them, in this order:
  1. **Where you are.** What ran just before this step, which function this is, and its job
     in the whole workflow. Name the previous step's result that this code receives.
  2. **What the code does.** The lines in order, one sentence each for the important ones.
     Name the line by what it does, not only by its number.
  3. **In this run.** The real values the recording holds, as the page prints them, and the
     variable to look at in the Variables pane to see each one.
  4. **Why it is built this way** (only when it helps): the problem this code prevents, or a
     result that surprised you. Say when the run shows a weakness.

## Words

- Define each term the first time the walkthrough uses it, in one sentence: "A Leg is one
  search of one source, for one condition of the question." After that, use the term as it
  is. Do not define it again, and do not change it for a synonym.
- Take terms from the project's `GLOSSARY.md`; when there are more than one, `GLOSSARY-MAP.md`
  points to the right one. With no glossary, use the code's own names (`fuse`, `Leg`), and
  write each name from the code in backticks.
- Explain any language feature a new reader may not know when it first matters:
  `async`/`await`, a closure, a decorator, `try`/`finally`.

## Sentences: ASD-STE100 Simplified Technical English

- One idea per sentence. At most 20 words in a sentence, and at most 6 sentences in a paragraph.
- Use the active voice: "The planner writes the form", not "The form is written".
- Use the present tense for what the code does, and the past tense for what this run did.
- Use one word for one meaning, and one meaning for one word.
- Use simple verbs, not phrasal verbs: "start", not "kick off"; "find", not "look up".
- Keep "the", "a" and "an". Do not use idioms, jokes, or words such as "simply" or "just".
- Write a list as separate sentences, not as one sentence with many clauses.
