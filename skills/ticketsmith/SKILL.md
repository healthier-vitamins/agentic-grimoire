---
name: ticketsmith
description: Forge a Jira ticket template that explains the work, with an item table and one sub-task per item, from a description or the codebase.
argument-hint: "[one-sentence description]"
disable-model-invocation: true
---

The ticket **explains the work as a whole** to a product owner, business analyst, or
project manager: someone fluent in the product with no view of the code. A short
explanation says what the work is, why, and where it stands. The work then breaks into
**items**: a table on the parent ticket, and one sub-task per item. The shape is in
[`references/ticket.md`](references/ticket.md).

> **Model requirement (hard):** a subagent drafts the ticket (Step 5), pinned to Claude
> Sonnet or GPT-5.5 (medium effort), whatever the orchestrator's model.
> - **Claude Code:** `Agent` tool with `model: sonnet`.
> - **Codex:** a custom agent with `model = "gpt-5.5"`,
>   `model_reasoning_effort = "medium"`.

## Standards

- **What the ticket contains:** [`references/ticket.md`](references/ticket.md) (the
  template) and [`references/house-style.md`](references/house-style.md) (what stays,
  what goes, the cut).
- **How each ticket sentence reads:** the `scribe` skill (`SKILL.md` plus
  `references/ai-tells.md`). The reader is the product owner, analyst, or project manager
  named above.
- **How you talk to the user:** every preview, question, and summary in ASD-STE100
  Simplified Technical English. Give a little context first, then short sentences in the
  active voice, one idea each. (Folded in from Matt Pocock's `wait-what`.)

## Step 1: Get the seed

Use `$ARGUMENTS` as the description. When it is empty, ask the user for a one-sentence
description.

**Done when:** you hold a description.

## Step 2: Ensure the dependencies are installed

Check for two skills:

- **`grilling`** (Matt Pocock's), which runs the Step 4 interview. It ships in the
  `mattpocock-skills` plugin and may be listed as `mattpocock-skills:grilling`.
- **`scribe`** (this repo's), which sets the ticket's prose. Look in
  `~/.claude/skills/scribe/` (Claude Code), `~/.agents/skills/scribe/` (Codex), or the
  active profile's `skills/scribe/`. Record the absolute path of its directory for Step 5.

For each one missing, show the user its install command and **ask before running it**. It
changes their global skill store:

```sh
# grilling: Claude Code, then Codex
claude plugin install mattpocock-skills@claude-plugins-official
codex plugin add mattpocock-skills@openai-curated-remote
# scribe
npx skills add healthier-vitamins/agentic-grimoire -g -s scribe
```

**Done when:** both skills are available, or the user declined an install. On a decline,
stop.

## Step 3: Scope the code (if available)

Run `git rev-parse --is-inside-work-tree`. Inside a repo, read the files, areas, and commits
the description names, to form two things:

- **Context assumptions:** how the relevant behaviour works today, in plain language.
- **Candidate done items:** which items the code or history shows as already done.

Read only what the description names. The Step 5 subagent reads deeper.

**Done when:** the context assumptions and candidate done items are written down, or the
step was skipped because there is no repo.

## Step 4: The interview (Matt Pocock's skill), run in-session

Invoke the `grilling` skill with the Skill tool, in this session. Pass it the description
(plus "in repo `<name>`" if Step 3 found one). `grilling` asks in **rounds**, at most five
questions per round, each with a recommended answer. Ticketsmith starts it and folds the
resolved decisions back into this flow. Point the interview at three things:

- **The why.** The goal behind the work, which the explanation needs.
- **The context.** Hand over Step 3's context assumptions and candidate done items, so
  the user confirms or corrects them. Draft only from confirmed context. An item counts
  as done once the user confirms it.
- **The fields** from `ticket.md`: issue type, parent, label, sprint, assignee, status,
  estimate.

**One ticket, one goal (re-align gate):** after the interview, check the resolved scope.
When it holds several distinct goals, list them, recommend one ticket per goal, and ask
which to draft first. When the user folds related work into one ticket instead, that work
goes in the template's *Also* section with its own sub-tasks.

**Done when:** every interview branch is resolved or the user said to proceed, every done
item is confirmed, and the scope holds one goal.

## Step 5: Draft the ticket in a pinned subagent

Spawn a subagent on the required model and pass it: the seed description, the confirmed
decisions and context, the repo path (if any), the **absolute paths to
`references/ticket.md` and `references/house-style.md`**, and the **absolute path to the
`scribe` directory** from Step 2. Instruct the subagent to:

1. **Ground, don't surface.** Read the repo to make the explanation and items accurate (use
   `Explore` for broader sweeps). Grounding informs the content; identifiers stay out of the
   ticket.
2. **Read `ticket.md`, `house-style.md`, and scribe's `SKILL.md` in full.** Fill
   `ticket.md`'s template, take content rules from `house-style.md`, and take wording from
   scribe. `house-style.md` §5 draws the identifier line: codebase-free, not domain-free.
3. **Draft for completeness.** Step 6 does the subtracting.
4. Return the full ticket text, sub-tasks included, in the reply. Write no file.

**Done when:** every section of the template is filled, every table row has a sub-task,
and every done item traces to the user's confirmation.

## Step 6: The cut

Run this in the main session. Read `references/house-style.md`, then apply §2's six
questions to **every line** of the draft: the title, the explanation, each table cell, and
each sub-task point. Delete a failing line whole rather than trimming it. Then run scribe's
cleanup pass over the survivors: edit them against scribe's `references/ai-tells.md`.

Two guards:

- **The floor (§4).** Stop before cutting the symptom, the ask, where it stands, a fact
  that changes the approach, or a decision with its owner and date.
- **Question 6 is the stop rule.** Keep a line whenever you can name what breaks without
  it.

Then re-read the result once against §1. If it still reads as a defence of an idea rather
than an account of the work, the genre is wrong and the cut is unfinished.

Write the cut ticket to `./<slug-from-title>.md` in the **current working directory**. If
that file exists, add a suffix: `<slug>-2.md`, `<slug>-3.md`, and so on.

**Done when:** every remaining line survives all six questions, every pattern in scribe's
`references/ai-tells.md` has been checked, and the file is written.

## Step 7: Preview

Show the user the cut ticket as it will look: the tree (parent and sub-tasks), the fields,
the explanation, the table, and each sub-task. When the session can publish an HTML page,
show it there; otherwise print it in the chat. Report the draft's line count and the cut's.
Apply every change the user asks for to both the preview and the file.

**Done when:** the user approves the ticket.

## Step 8: Hand off

Report the template's file path. The template is the deliverable. Recommend helping the
user set up a Jira connection, so they can create the tickets from it.

**Done when:** the file path is reported and the Jira setup is offered.
