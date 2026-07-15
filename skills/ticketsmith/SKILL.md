---
name: ticketsmith
description: Forge a Jira user story with checkbox acceptance criteria (doubling as a status update) from a description or codebase context, grilled for accuracy.
argument-hint: "[one-sentence description]"
disable-model-invocation: true
---

The **user story is the highlight**. Write it so a product owner, business analyst, or
project manager with no visibility into this project catches up fast — the why, the
domain, and where it stands. The **acceptance criteria are checkboxes** that carry the
status: `[x]` done, `[ ]` outstanding. Those two sections are the whole ticket.

> **Model requirement (hard):** the ticket **draft** must be produced by a
> subagent pinned to **Claude Sonnet 5** or **GPT-5.4 (medium effort)** —
> nothing else. Do not draft the ticket in the main session; delegate it (Step 5)
> so the model is enforced regardless of the orchestrator's model.
> - **Claude Code:** `Agent` tool with `model: sonnet` (i.e. `claude-sonnet-5`).
> - **Codex:** a custom agent with `model = "gpt-5.4"`,
>   `model_reasoning_effort = "medium"`.

## Step 1 — Get the seed

Use `$ARGUMENTS` as the description. If empty, ask the user for a one-sentence
description of what they want built. Do not proceed without it.

## Step 2 — Ensure grill-me is installed

Check for Matt Pocock's `grill-me` skill (`~/.claude/skills/grill-me/` for
Claude Code, `~/.agents/skills/grill-me/` for Codex, or the active profile's
`skills/grill-me/`). If it is **missing**, show the user the
install command and **ask before running it** — it mutates their global skill
store:

```sh
npx skills add mattpocock/skills --skill=grill-me
```

Run it only on the user's yes. If they decline, stop.

## Step 3 — Scope the code (if available)

Run `git rev-parse --is-inside-work-tree`. If inside a repo, read the files and
areas the description names to form two things:

- **Context assumptions** — how the relevant behaviour works today, in plain language.
- **Candidate done-state** — which acceptance criteria the code already appears to satisfy.

Stay scoped to what the description names; deeper reads happen in the Step 5 subagent.
If not in a repo, skip.

**Done when:** context assumptions and candidate done-state are captured, or the step was
skipped because there is no repo.

## Step 4 — grill-me interview (Matt Pocock's skill), advisory handoff

Hand the interview to `grill-me`. Give the user a one-line seed (the description
+ "in repo `<name>`" if Step 3 found one) and ask them to run `/grill-me`. Wait
for the grilling session to finish, then fold the resolved decisions back into
this flow. Do **not** re-implement the interview inline — `grill-me` drives the
questioning.

**Goal seed:** direct `grill-me` to surface the **main goal / why** behind the
request — the benefit the user story's "so that" needs — not just the what.

**Context-correctness gate:** when Step 3 scoped code, hand the context
assumptions and candidate done-state to `grill-me` as well, so the user
**confirms or corrects** them. Draft only from confirmed context; a criterion
counts as done only once the user confirms it.

**One ticket, one goal (re-align gate):** after `grill-me` finishes, before
Step 5, check the resolved scope. If it contains several distinct goals,
**stop** — list them, recommend one ticket per goal, and ask which to draft
first. Draft only the chosen single-goal ticket in Step 5; the rest are separate
ticketsmith runs.

## Step 5 — Draft the ticket in a pinned subagent

Spawn a subagent on the required model (see the model requirement above) and pass
it: the seed description, the confirmed `grill-me` decisions, the confirmed
context and done-state, and the repo path (if any). Instruct the subagent to:

1. **Ground, don't surface.** Read the repo to make the story and criteria
   accurate (use `Explore` for broader sweeps). Grounding informs the content
   only — it never licenses identifiers in the ticket.
2. **Write for a reader who has never opened the repo.** Both sections are
   plain-language and **identifier-free**: no file paths, module or framework
   names, or code identifiers anywhere.
3. Fill this template — the two sections are the whole ticket:

   ```
   # <concise title>

   ## User story
   As a <role>, I want <capability> so that <benefit>.

   <2-3 plain sentences of context: the why, the domain, and where it stands —
   enough for a product owner or business analyst with no project visibility to
   catch up fast.>

   ## Acceptance criteria
   - [x] <criterion the confirmed context shows already done>
   - [ ] <criterion still outstanding, verifiable, plain language>
   ```

   Mark `[x]` only for criteria confirmed done in the grill; every other
   criterion is `[ ]`.
4. Write it to `./<slug-from-title>.md` in the **current working directory**
   (the user's folder, not a scratchpad). If that file already exists, suffix to
   avoid clobbering: `<slug>-2.md`, `<slug>-3.md`, … Return the full ticket text
   and the path it wrote.

**Done when:** the subagent returns the full ticket text and the path it wrote.

## Step 6 — Emit

Print the ticket the subagent returned and report the file path.

**Criterion:** a `.md` ticket file exists in the current folder (suffixed per
Step 5.4, never clobbering) whose only sections are an identifier-free **User
story** and checkbox **Acceptance criteria**, with `[x]` limited to
grill-confirmed done criteria. Produced by a Sonnet-5 / GPT-5.4-medium subagent
from the `grill-me` interview and confirmed context, with the same content
printed in the chat.
