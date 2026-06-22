# teach-publish

An agent skill that publishes a [`teach`](https://github.com) course folder
(`lessons/ reference/ assets/`) to a **private** Cloudflare Pages site — so you can read
your interactive HTML lessons on your phone, with full fidelity (live quizzes and all),
no computer left running, gated to your email only, on the free tier.

It's a thin downstream stage for the `teach` skill: `teach` builds lessons in a workspace,
`teach-publish` mirrors that workspace to the web.

## Install

Drop this folder into your skills directory:

```
~/.claude/skills/teach-publish/
~/.codex/skills/teach-publish/
```

Then trigger it by asking Claude or Codex to "publish this course" / "put my lessons online", or run
the driver directly:

```bash
bash ~/.claude/skills/teach-publish/publish.sh
# or
bash ~/.codex/skills/teach-publish/publish.sh
```

## What it does

```
cd <course-or-repo>  →  publish.sh  →  https://<your-project>.pages.dev/<course>/
```

1. Auto-detects the course (cwd if it's a teach workspace, else the sole folder under
   `./teach/`).
2. Mirrors its web parts into a shared local staging site (`~/.teach-site/`), one subfolder
   per course, excluding private teaching state (MISSION/NOTES/RESOURCES/learning-records).
3. Rebuilds a portal index linking every course.
4. Uploads with `wrangler pages deploy` and prints the URL.

Multiple courses share **one** site and **one** privacy gate — add a course by running the
skill from its repo; it's instantly live and already private.

## Shareable by design

This folder contains **zero personal data** — safe to commit, copy, or publish as-is. The
only per-user state lives outside it:

- `~/.config/teach-publish/config` — your Cloudflare project name (written on first run).
- Your Cloudflare account — the privacy gate and your allowed email.

## First-time setup

One time, ever: a free Cloudflare account, `npx wrangler login`, pick a project name, and a
one-time Access gate. The driver detects a fresh install and walks you through it. Full
runbook: [`SETUP.md`](./SETUP.md).

## Requirements

- Node (for `npx wrangler`) and Python 3 (stdlib only). `rsync`.
- A free Cloudflare account.
