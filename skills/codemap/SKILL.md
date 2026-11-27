---
name: codemap
description: Map a whole codebase as areas and sections, with statecharts where the code keeps state, and a copyable /codewalk prompt per section.
argument-hint: "[project path]"
disable-model-invocation: true
---

The user is new to a codebase and wants the **overview** first: a mindmap of its areas and
sections, each section with its job, entry points, key files and size, and a statechart
where the code has a real state machine. Each section's button copies a `/codewalk` prompt,
so the user deep-dives one section at a time, only the ones they pick. The map stays cheap:
it never runs a codewalk itself.

**Iron rule: write only to `<project>/.codemap/`.** The scripts add `.codemap/` to
`.git/info/exclude` on first use.

`<skill>` below is this skill's directory. Languages: Python, JavaScript, TypeScript.

## Vocabulary

- **Area**: a top-level branch of the map, a group of sections (Turn path, Delivery).
- **Section**: one unit a single codewalk can cover: a job, entry points, files. Its
  **slug** is the codewalk's folder name.
- **Facts**: what `scan.py` computes: files, line counts, symbols with lines, imports,
  state lists. Never write a fact by hand.
- **Citation**: a `path:line` or `path::Symbol` in the map, checked by the build.

## Step 1: Scan

```sh
uv run <skill>/scripts/scan.py --root <project>
```

**Done when:** `.codemap/facts.json` exists and the line it prints names the file and line
totals.

## Step 2: Read and group

Read the project's own map first (README, docs, module docstrings), then the code: from each
entry point (CLI commands, servers, exported functions), follow calls to see which files work
together. Group the files into sections of one job each, and the sections into areas. Use
the project's own terms for names. Read `facts.json` `states` for state machines: a state
list counts only when the code moves a record between its values (an `UPDATE ... SET status`,
an assignment, a setter). A list that is only read, or a value set nothing writes, gets no
statechart.

**Done when:** every source file outside tests is in exactly one section or set aside with a
reason, and each statechart candidate is kept with its transitions found or dropped with a
reason.

## Step 3: Confirm the grouping

Show the user, per area: each section's slug, one-line job, files, and any statechart's
states. Name the files set aside. Ask them to confirm, or to rename, merge, split, move or
drop. Redo Step 2 on their edits and show it again.

**Done when:** the user has confirmed the grouping as shown.

## Step 4: Write the map

Write `.codemap/map.json` in the shape of [map-format.md](references/map-format.md):
jobs, files, entry points by symbol, and for each kept statechart its `states_from` and
every transition with the `path:line` where it happens.

**Done when:** every section has a job, files and at least one entry point, and every
transition the code makes for a kept statechart is listed.

## Step 5: Build

```sh
uv run <skill>/scripts/build.py --root <project>
```

The build rescans, checks every citation, and writes `.codemap/map.html`. A section whose
`.codewalk/<slug>/page.html` exists gets a "walked" badge and a link to it. On exit 1, fix
each line it printed and build again.

**Done when:** the build exits 0.

## Step 6: Hand over

Publish `.codemap/map.html` as an artifact, then tell the user, in chat:

- the link;
- the files no section holds (the build prints them);
- that each section's button copies its `/codewalk` prompt, and "Copy map as text" copies
  the whole overview for a chat.

**Done when:** all three are in the reply.
