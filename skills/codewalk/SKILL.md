---
name: codewalk
description: Record a real run of a workflow — existing code, a diff, or a prototype not written yet — and publish it as a time-travel debugger page.
argument-hint: "[path | diff-ref | idea to prototype]"
disable-model-invocation: true
---

The user wants to *see* code run: the workflows it holds, a captioned walkthrough, and a
**time-travel debugger** — step into, over, out, back, or to the next stop, with every
variable's value at every step. The page replays a **recording** of one real run, so what
the user steps through is what actually happened.

**Iron rule: project files change only at Step 10, on the user's "apply".** Everything
before writes to `<project>/.codewalk/`, added to `.git/info/exclude` on first use.

Scripts live in this skill's `scripts/` folder; `<skill>` below is this skill's directory.

## Vocabulary

- **Workflow** — one end-to-end path from an entry point until it leaves the target. Say
  *workflow*, not chain or flow.
- **Recording** — the JSON one run produces: frames, steps, changed variables.
- **Stop** — a step the debugger's "next stop" lands on: the first run of a walkthrough
  step's lines, or a breakpoint function's call.
- **Staging** — `.codewalk/staging/<slug>/`, where prototype code lives before it is applied.

Rejected framings: the old *walk* (quiz-first) and *sweep* (chat trace) gears — a recording
shows real state, which neither could.

## Step 1 — Resolve the target

Fix one target and its branch:

| Branch | Argument | Code that runs |
|---|---|---|
| **existing** | a path or symbol | the project as it is |
| **diff** | `HEAD`, a SHA, `A...B`, or nothing with a dirty tree | the project as it is |
| **prototype** | an idea, or code not yet in the project | staging — read [staging.md](references/staging.md) |

Languages: Python, JavaScript, TypeScript. A target in any other language → tell the user
codewalk cannot record it, and stop.

**Done when:** one target, its branch, and every language it touches are named back to the
user in one line.

## Step 2 — Map the workflows

From the target's entry points (exported functions, route handlers, CLI commands, changed
lines of a diff), follow calls until they leave the target. Two entry points that never
converge are two workflows.

**Done when:** every entry point belongs to exactly one workflow, and each workflow lists its
functions in call order with `file:line`.

## Step 3 — Confirm the workflows

Show the map — per workflow: its name, its entry point, and its functions in call order with
`file:line` — and ask the user to confirm it, or to merge, split, drop, or add workflows.
Redo Step 2 on their edits and show the map again.

**Done when:** the user has confirmed the map as shown.

## Step 4 — Pick each workflow's entry

1. A **test** that runs through the workflow: a pytest node id, or `<test file>::<test name>`
   for the project's vitest or jest.
2. None → write a **driver** in `.codewalk/drivers/<workflow>.{py,ts,js}` that calls the
   workflow's entry point with realistic inputs.

**Done when:** every workflow has an entry, and its kind (test or driver) is noted for Step 9.

## Step 5 — Gate the outside world

Runs are real by default. List every call in each workflow that writes to the outside world
— database writes, emails, payments, messages, file writes outside `.codewalk/` — and ask the
user, per call, real or fake. Fake only those the user picks, plus any service the run cannot
reach (no credentials, no network), and say which.

**Done when:** every outside-world write has the user's answer, and every fake is listed.

## Step 6 — Record

Run each entry with the project's own runtime, so its imports resolve:

```sh
<project python> <skill>/scripts/record_py.py <flags>   # Python 3.12+
node <skill>/scripts/record_js.mjs <flags>              # JS/TS, Node 22+

<flags> = --root <project> --watch <paths…> --entry <test | driver> \
          --out .codewalk/recordings/<workflow>.json
```

`--watch` is the target's files and folders: code outside them runs without being stepped
into, the way a debugger's "just my code" steps over libraries. A `.ts` driver runs through
the project's `tsx` when installed. A run that fails still records — the page shows where it
raised.

**Done when:** every workflow has a recording with at least one step, and its exit status is
noted.

## Step 7 — Write the walkthrough

Per workflow, write `.codewalk/walkthrough/<workflow>.json` in the shape of
[page-format.md](references/page-format.md): the confirmed map from Step 3, the fakes from
Step 5, then one walkthrough step per idea — a line range and a caption saying *why*.

**Done when:** every workflow has a walkthrough, and every range in it lies inside a file its
recording ran.

## Step 8 — Build

```sh
uv run <skill>/scripts/build.py --root <project> --title "<title>"
```

The build checks Step 7's ranges, hides secrets, and writes `.codewalk/page.html`. It fails
over 14 MB; then narrow `--watch` and re-record.

**Done when:** the build exits 0.

## Step 9 — Publish

Publish `.codewalk/page.html` as an artifact, then tell the user, in chat:

- the link;
- every hidden variable the build printed — they may want more hidden before sharing;
- each workflow's entry kind (test or driver), and every fake.

**Done when:** all three are in the reply.

## Step 10 — Apply (prototype only, on the user's "apply")

Copy each staged file to its mirrored path in the project, then run the project's own
validation for those files.

**Done when:** every staged file is in place and validation passes — or its failures are
reported in full.
