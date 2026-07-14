---
name: ticketsmith
description: Turn a one-sentence description into a grilled, repo-grounded Jira ticket.
argument-hint: "[one-sentence description]"
disable-model-invocation: true
---

> **Model requirement (hard):** the ticket **draft** must be produced by a
> subagent pinned to **Claude Sonnet 5** or **GPT-5.4 (medium effort)** —
> nothing else. Do not draft the ticket in the main session; delegate it (Step 5)
> so the model is enforced regardless of the orchestrator's model.
> - **Claude Code:** `Agent` tool with `model: sonnet` (i.e. `claude-sonnet-5`).
> - **Codex:** a custom agent with `model = "gpt-5.4"`,
>   `model_reasoning_effort = "medium"`.

Companion to `lathe` (which shapes the artifact) — this shapes the ticket.

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

## Step 3 — Detect the repo (light)

Run `git rev-parse --is-inside-work-tree`. If inside a repo, gather cheap seed
context only — `git ls-files | head` and `git log --oneline -5` — to orient the
interview. Deep reads happen in Step 5, inside the pinned subagent. If not in a
repo, skip. Done when: repo presence known and seed context captured, or the
step skipped.

## Step 4 — grill-me interview (Matt Pocock's skill), advisory handoff

Hand the interview to `grill-me`. Give the user a one-line seed (the description
+ "in repo `<name>`" if Step 3 found one) and ask them to run `/grill-me`. Wait
for the grilling session to finish, then fold the resolved decisions back into
this flow. Do **not** re-implement the interview inline — `grill-me` drives the
questioning.

**Goal seed:** when handing the seed to `grill-me`, direct it to surface the
**main goal / why** behind the request — the benefit the user story's "so that"
needs — not just the what.

**One ticket, one goal (re-align gate):** after `grill-me` finishes, before
Step 5, check the resolved scope. If it contains several distinct goals,
**stop** — list them, recommend one ticket per goal, and ask which to draft
first. Draft only the chosen single-goal ticket in Step 5; the rest are separate
ticketsmith runs.

## Step 5 — Draft the ticket in a pinned subagent

Spawn a subagent on the required model (see the model requirement above) and pass
it: the seed description, the resolved `grill-me` decisions, and the repo path
(if any). Instruct the subagent to:

1. **Ground, don't surface.** Read the repo to make the ticket accurate — read
   the files/dirs the description names (use `Explore` for broader sweeps). This
   grounding does **not** license identifiers in the plain sections.
2. Write every plain section for **a reader who has never opened the repo**:
   *User story*, *What needs to happen*, and *Acceptance criteria* are
   **identifier-free** — no file paths, module or framework names, or code
   identifiers. Confine all identifiers to a **Technical notes (for
   engineers)** section — and omit that section entirely when there is no repo.
3. Fill this template (keep **User story** and **What needs to happen** as the
   load-bearing sections):

   ```
   # <concise title>

   **Type:** Story | Bug | Task   **Labels:** <suggested>   **Estimate:** <t-shirt / points>

   ## User story
   As a <user>, I want <capability> so that <benefit>.

   ## What needs to happen
   - <plain-language point — identifier-free>
   - <plain-language point>

   ## Acceptance criteria
   - [ ] <verifiable outcome, in plain language>
   - [ ] <verifiable outcome>

   ## Technical notes (for engineers)
   - <grounding detail: real module/file names, reused utilities — the ONLY section where identifiers appear>
   - <omit this whole section when there is no repo>
   ```

4. Write it to `./<slug-from-title>.md` in the **current working directory**
   (the user's folder, not a scratchpad). If that file already exists, suffix to
   avoid clobbering: `<slug>-2.md`, `<slug>-3.md`, … Return the full ticket text
   and the path it wrote.

## Step 6 — Emit

Print the ticket the subagent returned and report the file path.

**Criterion:** a `.md` ticket file exists in the current folder (suffixed per
Step 5.4, never clobbering) whose plain sections are identifier-free per
Step 5.2. Produced by a Sonnet-5 / GPT-5.4-medium subagent from the `grill-me`
interview and repo context, with the same content printed in the chat.
