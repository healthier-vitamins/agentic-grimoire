---
name: ste
description: Rewrite the last message into ASD-STE100 Simplified Technical English.
argument-hint: "[excerpt to simplify — defaults to the whole last message]"
disable-model-invocation: true
---

# STE

Rewrite text that already exists into ASD-STE100 (Simplified Technical English). The thinking
is done. This is a transform, not a second attempt at the answer.

## The rule that protects the answer

Preserve every claim, condition, and qualifier. "Probably safe, but check the index rebuild"
becomes two sentences, never one confident sentence. A rewrite that drops a hedge has changed
the answer, and reads clean while being wrong.

## Scope

The argument names the target. With no argument, take the whole of the last message.

Rewrite: final answer prose; questions, option labels, and option descriptions; named
excerpts; plans, numbered steps, and runbooks.

Leave exactly as written: code, identifiers, file paths, and commands; verbatim quotes such
as error text, log output, and citations; anything already in STE.

## How

- One idea per sentence. Split compound sentences at the conjunction.
- Active voice. Name who acts.
- Simple tenses. Keep the articles.
- Noun clusters of three words or fewer.
- Steps become a numbered list, one instruction each.

## Done when

Every sentence in scope carries one idea, and every claim, condition, and qualifier from the
original survives somewhere in the rewrite.
