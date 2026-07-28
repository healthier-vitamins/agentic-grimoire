---
name: ticketsmith
description: Forge a Jira user story with checkbox acceptance criteria (doubling as a status update) from a description or codebase context, grilled for accuracy.
argument-hint: "[one-sentence description]"
disable-model-invocation: true
---

The **user story is the highlight**. Write it for a product owner, business
analyst, or project manager: someone fluent in the product but with no visibility
into the code. They get the why, the current behaviour, and where it stands. The
**acceptance criteria are checkboxes** that carry the status: `[x]` done, `[ ]`
outstanding. Those two sections are the whole ticket.

> **Model requirement (hard):** the ticket **draft** must be produced by a
> subagent pinned to **Claude Sonnet 5** or **GPT-5.5 (medium effort)**, nothing
> else. Do not draft the ticket in the main session. Delegate it (Step 5) so the
> model is enforced regardless of the orchestrator's model.
> - **Claude Code:** `Agent` tool with `model: sonnet` (i.e. `claude-sonnet-5`).
> - **Codex:** a custom agent with `model = "gpt-5.5"`,
>   `model_reasoning_effort = "medium"`.

## House style (ticket output)

**`references/house-style.md` is the standard.** Both the Step 5 drafter and the
Step 6 cut read it in full. It governs the ticket only, not this doc. The short
form:

- **A ticket is not a research report.** It answers what is wrong, what we will
  try, and how we will know. Nothing else.
- **The template is the whole ticket.** Never invent sections.
- **Add information, don't restate.** Cut any sentence that re-says the title or
  the story.
- **Speak the team's language.** No file, module, or function names. Product,
  vendor, and domain nouns the team says out loud stay.
- **Plain and pragmatic.** No emdashes, no hype, no hedging.

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
context and done-state, the repo path (if any), and the **absolute path to this
skill's `references/house-style.md`**. Instruct the subagent to:

1. **Ground, don't surface.** Read the repo to make the story and criteria
   accurate (use `Explore` for broader sweeps). Grounding informs the content
   only. It never licenses identifiers in the ticket.
2. **Read `house-style.md` in full** and write both sections to it. §5 is the
   identifier line: codebase-free, not domain-free.
3. **Write for a peer, not a stranger.** Draft for completeness here. Step 6 does
   the subtracting — do not try to be concise and complete in one pass.
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
5. Return the full ticket text in the reply. **Write no file** — Step 6 cuts the
   draft first, and only the cut ticket reaches the user's disk.

**Done when:** the subagent returns the full ticket text.

## Step 6: The cut

Run this in the main session, not a subagent. Read `references/house-style.md`,
then apply §2's six questions to **every line** of the returned draft, including
the title and each criterion. Delete a failing line whole rather than trimming it.

Two guards:

- **The floor (§4).** Stop before cutting the symptom, the ask, the done-check, a
  fact that changes the approach, or a decision with its owner and date.
- **Question 6 is the stop rule.** Keep a line whenever you can name what breaks
  without it.

Then re-read the result once against §1: if it still reads as a defence of an idea
rather than an instruction, the genre is wrong and the cut is unfinished.

Write the cut ticket to `./<slug-from-title>.md` in the **current working
directory** (the user's folder, not a scratchpad). If that file exists, suffix to
avoid clobbering: `<slug>-2.md`, `<slug>-3.md`, and so on.

**Done when:** every remaining line survives all six questions and the file is
written.

## Step 7: Emit

Print the cut ticket and report the file path. Report the draft's line count and
the cut's, so the user can see what the pass removed.

**Criterion:** a `.md` ticket file exists in the current folder (suffixed per Step
6, never clobbering) whose only sections are a **User story** and checkbox
**Acceptance criteria**, with `[x]` limited to grill-confirmed done criteria. It
was drafted by a Sonnet-5 / GPT-5.5-medium subagent from the `grill-me` interview
and confirmed context, then put through the Step 6 cut, and every surviving line
answers all six questions in `references/house-style.md` §2. The same content is
printed in the chat.
