---
name: codewalk
description: Record real runs of one section's workflows — existing code, a diff, or a prototype not written yet — and publish them as a chapter-stories page with a time-travel debugger.
argument-hint: "[codemap section prompt | path | diff-ref | idea to prototype]"
disable-model-invocation: true
---

The user wants to *see* one section of code run, deeply. The page tells each workflow as
**chapter stories**: one step per screen, with its code, the real values the run held there,
and one line on what happened. Any step opens the **time-travel debugger** at that point —
step into, over, out, back, or to the next stop, with every variable's value at every step.
The page replays a **recording** of one real run, so what the user reads is what actually
happened.

**Iron rule: project files change only at Step 10, on the user's "apply".** Everything
before writes to `<project>/.codewalk/<section>/`; `.codewalk/` is added to
`.git/info/exclude` on first use.

Scripts live in this skill's `scripts/` folder; `<skill>` below is this skill's directory.

## Vocabulary

- **Workflow** — one end-to-end path from an entry point until it leaves the target. Say
  *workflow*, not chain or flow.
- **Recording** — the JSON one run produces: frames, steps, changed variables.
- **Section** — the part of the codebase one page covers, named by a slug: one codemap
  section, or the target the user named. Its files live in `.codewalk/<section>/`.
- **Chapter** — one idea of a workflow, told in 1 to 7 walkthrough steps.
- **Stop** — where a walkthrough step is anchored in the recording: its call's first run of
  the step's lines ([page-format.md](references/page-format.md) has the rule). The debugger
  opens there, and "next stop" lands on every stop and every breakpoint call.
- **Staging** — `.codewalk/<section>/staging/<slug>/`, where prototype code lives before it is applied.

Rejected framings: the old *walk* (quiz-first) and *sweep* (chat trace) gears — a recording
shows real state, which neither could.

## Step 1 — Resolve the target

Fix one target, its branch, and its section slug:

| Branch | Argument | Code that runs |
|---|---|---|
| **section** | a codemap prompt: one section, its slug, entry points and files | the project as it is |
| **existing** | a path or symbol | the project as it is |
| **diff** | `HEAD`, a SHA, `A...B`, or nothing with a dirty tree | the project as it is |
| **prototype** | an idea, or code not yet in the project | staging — read [staging.md](references/staging.md) |

A codemap prompt fixes the target to that section alone: its entry points and its files.
Walk only that section; code it calls in other sections runs unwatched. Take the slug from the
prompt as given: codemap marks the section as walked by finding `.codewalk/<slug>/page.html`.
For any other branch, make the slug from the target's name in kebab-case (`upload-retry`).

Languages: Python, JavaScript, TypeScript. A target in any other language → tell the user
codewalk cannot record it, and stop.

**Done when:** one target, its branch, its slug, and every language it touches are named back
to the user in one line.

## Step 2 — Map the workflows

From the target's entry points (a section's listed entry points, exported functions, route
handlers, CLI commands, changed lines of a diff), follow calls until they leave the target. Two entry points that never
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
2. None → write a **driver** in `.codewalk/<section>/drivers/<workflow>.{py,ts,js}` that calls the
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
          --out .codewalk/<section>/recordings/<workflow>.json
```

`--watch` is the target's files and folders: code outside them runs without being stepped
into, the way a debugger's "just my code" steps over libraries. The run waits while the
recorder prints, so timeouts and budgets can fire that would not unrecorded; the page shows
how much time the recorder added to each call. Add `--exact-values` (Python) to print every
value at every step instead of reusing unchanged ones: exact, but slower. A `.ts` driver runs through
the project's `tsx` when installed. A run that fails still records — the page shows where it
raised.

**Done when:** every workflow has a recording with at least one step, and its exit status is
noted.

## Step 7 — Write the walkthrough

Per workflow, write `.codewalk/<section>/walkthrough/<workflow>.json` in the shape of
[page-format.md](references/page-format.md): the confirmed map from Step 3, the fakes from
Step 5, then the walkthrough as chapters — one chapter per idea, 1 to 7 steps each. A
section's workflows together take up to about 13 chapters. Each step is a line range with the
layered texts [captions.md](references/captions.md) gives (`title`, `gist`, `where`, `what`,
`run`, optional `why`), written for a reader new to the code, in Simplified Technical
English, with every term defined where it first appears. Mark the values that came in and
went out with `came_in` and `went_out`.

**Done when:** every workflow has a walkthrough, every chapter holds 1 to 7 steps, every range
lies inside a file its recording ran, and every step has all the texts captions.md requires.

## Step 8 — Build

```sh
uv run <skill>/scripts/build.py --root <project> --title "<title>" --section <slug>
```

The build checks Step 7's walkthroughs and prints each step's anchor: its function, which
call of how many, the stop, and that call's arguments. Read each anchor against the step's
`run` text. When a step anchored to the wrong call (the owner's message where the step is about
a stranger's tap), add `"call": N` to the step and build again. It also hides secrets (secret-named variables and fields, key-shaped
strings, secret environment values), and writes `.codewalk/<section>/page.html`. The page shows the
first 20,000 characters of each value; every value in full goes to `.codewalk/<section>/texts.json`,
and each variable's "ask" link copies a question naming its place there. It fails over
14 MB; then narrow `--watch` and re-record.

**Done when:** the build exits 0, and every step's printed anchor is the call its text
describes.

## Step 9 — Publish

Publish `.codewalk/<section>/page.html` as an artifact, then tell the user, in chat:

- the link;
- every hidden variable the build printed — they may want more hidden before sharing;
- each workflow's entry kind (test or driver), and every fake.

**Done when:** all three are in the reply.

## Step 10 — Apply (prototype only, on the user's "apply")

Copy each staged file to its mirrored path in the project, then run the project's own
validation for those files.

**Done when:** every staged file is in place and validation passes — or its failures are
reported in full.
