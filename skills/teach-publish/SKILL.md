---
name: teach-publish
description: Publish a teach/ course folder to a private Cloudflare Pages site so lessons are viewable on a phone. Use when the user wants to publish or deploy a course, put lessons online privately, push a teach workspace to Cloudflare, or read their lessons on mobile.
argument-hint: "[--slug name] [--course dir] [--no-deploy]"
---

# teach-publish

Sync a `teach` course folder (`lessons/ reference/ assets/`) to the user's **private**
Cloudflare Pages site. The whole job is one script — `publish.sh`. Your role is to run it
and report the URL it prints.

## Do this

From the course's repo (or the workspace folder itself), run the driver:

```bash
if [ -n "${CLAUDE_SKILL_DIR:-}" ]; then
  bash "$CLAUDE_SKILL_DIR/publish.sh"
elif [ -f "$HOME/.codex/skills/teach-publish/publish.sh" ]; then
  bash "$HOME/.codex/skills/teach-publish/publish.sh"
else
  bash "$HOME/.claude/skills/teach-publish/publish.sh"
fi
```

It auto-detects the course (cwd if it's a teach workspace, else the sole folder under
`./teach/`). Override when needed:

- `--course <dir>` — publish a specific folder.
- `--slug <name>` — set the URL subfolder (default: the folder's name).
- `--no-deploy` — build the local staging site only (no upload); good for a dry run.

**Done when:** `publish.sh` exits 0 and prints a `https://<project>.pages.dev/<slug>/`
URL that loads the course. Report that URL. (Not just "deployed.")

## First run on a machine (one time, ever)

If `publish.sh` stops asking for `wrangler login` or a project name, the user hasn't set
up Cloudflare yet. **Read `SETUP.md`** and walk them through it — account, login, project
name, and the one-time Access gate that makes the site private. After that, every publish
is just the one command above.

The browser login and the dashboard gate are human steps — you can detect and explain
them, but you can't click them. Hand those to the user.
