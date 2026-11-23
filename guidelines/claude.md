# CLAUDE.md — agentic-grimoire guidelines

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## Validation

Before finishing coding work, run the validation commands that match the changed scope
(project scripts first, else the installed tool directly):

- JS/TS: `lint`, `typecheck`, `format:check`, `test` scripts — or `npx eslint .`, `npx tsc --noEmit`, `npx prettier --check .`
- Python: `uv run ruff check .`, `uv run ruff format --check .`, `uv run pyright`, `uv run pytest`

Do not finish with known safe-to-fix issues in the changed scope. Do not weaken rules or hide failures.

## Commits

End every commit message with Claude Code's classic attribution, exactly:

```
🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

This replaces the model-named `Co-Authored-By` line and the `Claude-Session` session-id/URL
trailer the harness suggests — add neither.
(Codex has no default co-author trailer, so it attaches nothing — that is expected.)

## Model Selection

For cost efficiency without quality loss, use the `opusplan` alias (`/model opusplan`):
Opus plans and reviews, then auto-switches to Sonnet for execution within the same session.
Keep planning and final review on the top model and let Sonnet handle mechanical execution.
Do not downgrade further (e.g. Haiku) for non-trivial work — failed loops cost more than they save.

Route subagents by difficulty — each agent's own `model` sets its cost, whatever model the
main session runs:

- research and hard analysis → `researcher` (Opus)
- implementing an already-decided plan → `executor` (Sonnet)
- codebase search → `Explore` (Haiku), rather than reading widely inline, so the
  orchestrator's context stays clean

Keep planning and review on the main thread.

## Usage Budget

The 5-hour usage limit is shared by the main session and every subagent. Size large work
before it starts, so one request never spends the whole limit without warning. Normal work
gets no extra steps: these rules apply only above the threshold.

**Threshold.** Any one of these:

- more than 4 subagents in total, or more than 3 running at once;
- a Workflow run;
- the same heavy task repeated over more than 5 items (questions, files, pages, PRs).

**Above the threshold, estimate first.** Before the first agent starts, tell the user what
runs (agent count, model, how many at once), the rough token total, and the share of the
5-hour limit it may take. Per-agent figures, measured 2026-11-20:

- search or a short read: 30k to 60k tokens;
- read, write and verify one section: 150k to 300k tokens;
- work that views PDF pages or screenshots as images: the top of that range or more.

On 2026-11-20, 16 Opus agents used up a whole 5-hour window, an estimated 3 to 4 million
tokens. Below about 1 million tokens, state the estimate and proceed. Above it, wait for a
go-ahead, then build one unit first and report its measured cost (from the agent's usage
line) before starting the rest in parallel.

**Save by routing, not by cutting.** Keep quality steps. Save tokens this way instead:

- Keep each agent on its route above. Override a writer to Opus only when the step needs
  judgement, and say why.
- Run at most 4 agents at once.
- Subagents do not start their own subagents unless the brief allows it.

**Other heavy runs.** State their cost up front too:

- `/loop`, babysit or Monitor runs left unattended;
- render-and-view loops over many pages or screenshots;
- long web crawls;
- repeated reads of large files into the main session.

**Limit hit mid-run.** Work the agents saved stays on disk. After the reset, resume each
stopped agent with SendMessage instead of starting fresh ones.

## Keystone

Invoke the `keystone` skill before implementing non-trivial logic, structuring a module,
or judging whether existing code reads well — it carries the reading standard all code is
written to. React components, pages, and features take `keystone-react` on top of it.
Size rules decide how much code there is; Keystone decides how it reads. When they pull apart,
cut lines and keep Keystone's plain loops, full names, and worked-example docstrings.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked; no abstractions for single-use code.
- No "flexibility" that wasn't requested; no error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

- Don't "improve" adjacent code, comments, or formatting; don't refactor what isn't broken.
- Match existing style. If you notice unrelated dead code, mention it — don't delete it.
- Remove only the imports/variables YOUR changes made unused.
- The test: every changed line traces directly to the request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.** Transform tasks into verifiable goals
("fix the bug" → "write a failing test that reproduces it, then make it pass"). For
multi-step work, state a brief plan with a verify step per step.

## 5. Design Patterns

Reach for an established Gang-of-Four / architectural pattern before inventing structure —
don't build a bespoke solution a reviewer must reverse-engineer.

## 6. Close the Loop

**Report answers, never errands.** When a fact is reachable, fetch it in the same turn; when a
finding raises a new question, check that too, until each lead ends in a fact or a real blocker.

- Look before saying "not found" or "I don't know": the repo, local files, connected accounts
  (mail, calendar, drive), signed-in sites in the browser, then the web. When unsure of a fact,
  look it up instead of guessing or asking.
- Examples: a config names another file → open it; an email cites a deadline → check the
  calendar; a docs page names a version → check what's installed.
- Verify before handing over: run it, open the page, read back the live copy.
- Hand the user only what is theirs: their decisions, and the actions the guardrails reserve
  for them (sending, submitting, buying, changing settings, logins, 2FA, CAPTCHAs). Ask, then
  keep working on the rest.

## Context7

Use the `context7` tool for library/framework/API documentation, setup, and configuration
steps. Do not rely on memory for library versions or APIs when verification is possible.

## Shell Tool Preferences

Prefer `fd` over `find` and `rg` over `grep`. If either is missing, say so and ask before installing.
