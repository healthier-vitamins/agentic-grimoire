---
name: ticketsmith
description: Forge a Jira user story with checkbox acceptance criteria (doubling as a status update) from a description or codebase context, grilled for accuracy.
argument-hint: "[one-sentence description]"
disable-model-invocation: true
---

The **user story is the highlight**. Write it so a product owner, business analyst,
or project manager with no visibility into this project catches up fast: the why,
the domain, and where it stands. The **acceptance criteria are checkboxes** that
carry the status: `[x]` done, `[ ]` outstanding. Those two sections are the whole
ticket.

> **Model requirement (hard):** the ticket **draft** must be produced by a
> subagent pinned to **Claude Sonnet 5** or **GPT-5.4 (medium effort)**, nothing
> else. Do not draft the ticket in the main session. Delegate it (Step 5) so the
> model is enforced regardless of the orchestrator's model.
> - **Claude Code:** `Agent` tool with `model: sonnet` (i.e. `claude-sonnet-5`).
> - **Codex:** a custom agent with `model = "gpt-5.4"`,
>   `model_reasoning_effort = "medium"`.

## House style (ticket output)

The Step 5 subagent writes the ticket to these rules. They govern the drafted
ticket only, not this doc.

- **Add information, don't restate.** The context sentences must give the reader
  something the seed did not: the domain, the why, current behaviour, where it
  stands. Cut any sentence that only re-says the title or user story.
- **Concise over complete.** Explain enough for an outsider to catch up, then
  stop. Prefer fewer, denser sentences.
- **No emdashes.** Use full stops, commas, or parentheses. Emdashes read as AI
  boilerplate.
- **Pragmatic and plain.** State facts directly. No hype, no filler ("robust",
  "seamless", "it's worth noting"), no hedging.

**Worked example.**

Seed: research undesired GenAI-search responses for off-topic queries like "who
is lee kuan yew".

Too fluffy (reject):

> As a partner-facing user of the GenAI Search feature, I want the search to
> recognise when my query isn't actually asking to find a partner organisation,
> so that I don't get a list of irrelevant, noisy results that merely share a few
> words with my question.
>
> GenAI Search is meant to help people find partner organisations using natural
> language, not to answer general knowledge questions. Right now, a query like
> "who is lee kuan yew" — a question about Singapore's first Prime Minister, not a
> search for a partner — returns a cluttered list of partner records that happen
> to contain the words "lee", "kuan", or "yew" somewhere in their data. This same
> weakness likely affects other loosely-matching or off-topic queries too,
> undermining trust in the feature's results.

Right (accept):

> As a partner-facing user of GenAI Search, I want the search to tell when my
> query is not looking for a partner organisation, so that off-topic questions
> stop returning noisy, irrelevant matches.
>
> GenAI Search finds partner organisations from natural-language queries. It is
> not a general-knowledge tool. Today a query like "who is lee kuan yew" returns
> partner records that merely contain the words "lee", "kuan", or "yew", because
> matching is purely lexical. Other off-topic queries hit the same gap and erode
> trust in results.

The reject spells out who Lee Kuan Yew is, restates the story, and hedges. The
accept names the real cause (lexical matching) and stops.

## Step 1: Get the seed

Use `$ARGUMENTS` as the description. If empty, ask the user for a one-sentence
description of what they want built. Do not proceed without it.

## Step 2: Ensure grill-me is installed

Check for Matt Pocock's `grill-me` skill (`~/.claude/skills/grill-me/` for Claude
Code, `~/.agents/skills/grill-me/` for Codex, or the active profile's
`skills/grill-me/`). If **missing**, show the user the install command and **ask
before running it**. It mutates their global skill store:

```sh
npx skills add mattpocock/skills --skill=grill-me
```

Run it only on the user's yes. If they decline, stop.

## Step 3: Scope the code (if available)

Run `git rev-parse --is-inside-work-tree`. If inside a repo, read the files and
areas the description names to form two things:

- **Context assumptions:** how the relevant behaviour works today, in plain
  language.
- **Candidate done-state:** which acceptance criteria the code already appears to
  satisfy.

Stay scoped to what the description names. Deeper reads happen in the Step 5
subagent. If not in a repo, skip.

**Done when:** context assumptions and candidate done-state are captured, or the
step was skipped because there is no repo.

## Step 4: grill-me interview (Matt Pocock's skill), advisory handoff

Hand the interview to `grill-me`. Give the user a one-line seed (the description,
plus "in repo `<name>`" if Step 3 found one) and ask them to run `/grill-me`. Wait
for the grilling session to finish, then fold the resolved decisions back into
this flow. Do **not** re-implement the interview inline; `grill-me` drives the
questioning.

**Goal seed:** direct `grill-me` to surface the **main goal / why** behind the
request, the benefit the user story's "so that" needs, not just the what.

**Context-correctness gate:** when Step 3 scoped code, hand the context
assumptions and candidate done-state to `grill-me` too, so the user **confirms or
corrects** them. Draft only from confirmed context. A criterion counts as done
only once the user confirms it.

**One ticket, one goal (re-align gate):** after `grill-me` finishes, before Step
5, check the resolved scope. If it contains several distinct goals, **stop**: list
them, recommend one ticket per goal, and ask which to draft first. Draft only the
chosen single-goal ticket in Step 5. The rest are separate ticketsmith runs.

## Step 5: Draft the ticket in a pinned subagent

Spawn a subagent on the required model (see the model requirement above) and pass
it: the seed description, the confirmed `grill-me` decisions, the confirmed
context and done-state, and the repo path (if any). Instruct the subagent to:

1. **Ground, don't surface.** Read the repo to make the story and criteria
   accurate (use `Explore` for broader sweeps). Grounding informs the content
   only. It never licenses identifiers in the ticket.
2. **Write for a reader who has never opened the repo.** Both sections are
   plain-language and **identifier-free**: no file paths, module or framework
   names, or code identifiers anywhere.
3. **Follow the House style above** for both sections: add information rather than
   restate, stay concise, no emdashes, plain and pragmatic.
4. Fill this template. The two sections are the whole ticket:

   ```
   # <concise title>

   ## User story
   As a <role>, I want <capability> so that <benefit>.

   <2-3 plain sentences of context per the House style: the why, the domain, and
   where it stands.>

   ## Acceptance criteria
   - [x] <criterion the confirmed context shows already done>
   - [ ] <criterion still outstanding, verifiable, plain language>
   ```

   Mark `[x]` only for criteria confirmed done in the grill. Every other criterion
   is `[ ]`.
5. Write it to `./<slug-from-title>.md` in the **current working directory** (the
   user's folder, not a scratchpad). If that file already exists, suffix to avoid
   clobbering: `<slug>-2.md`, `<slug>-3.md`, and so on. Return the full ticket
   text and the path it wrote.

**Done when:** the subagent returns the full ticket text and the path it wrote.

## Step 6: Emit

Print the ticket the subagent returned and report the file path.

**Criterion:** a `.md` ticket file exists in the current folder (suffixed per Step
5.5, never clobbering) whose only sections are an identifier-free **User story**
and checkbox **Acceptance criteria**, with `[x]` limited to grill-confirmed done
criteria. The output follows the House style (no emdashes, no fluff). Produced by
a Sonnet-5 / GPT-5.4-medium subagent from the `grill-me` interview and confirmed
context, with the same content printed in the chat.
