# agentic-grimoire

A collection of agent **skills** plus the guideline block they install into your
Claude Code and Codex config. Onboarding is one `npx` line and one or two slash commands —
no Makefile, no build step.

## Onboard

```sh
# 1. Install the skills into the central store (~/.agents/skills) and symlink them
#    into the conventional profiles (Claude Code + Codex). Dropping --yes lets the CLI
#    show an interactive multi-select picker so you choose which skills to install.
npx skills add healthier-vitamins/agentic-grimoire --global -a claude-code codex

# 2. Splice the guideline block into ~/.claude/CLAUDE.md AND ~/.codex/AGENTS.md
#    (append-only, idempotent — your existing content is preserved).
/setup-agentic-grimoire

# 3. Optional: extend to the custom profiles ~/.claude-personal and ~/.claude-sec
#    (symlink the store into them + splice their CLAUDE.md).
/link-agentic-grimoire-custom
```

**In the step 1 picker, always keep the four management skills selected —
`setup-agentic-grimoire`, `sync-agentic-grimoire`, `link-agentic-grimoire-custom`, and
`uninstall-agentic-grimoire`.** They are the machinery that splices the guideline block,
updates/prunes, and tears everything down; deselecting them breaks setup, update, and
uninstall. The picker needs a real terminal — in a non-TTY/CI shell, add `--yes` (installs
all) or `--skill <name>` to select non-interactively.

Steps 2 and 3 are slash commands you run **inside** Claude Code — they ship as skills, so
step 1 installs them. The first run is worth doing interactively so you can eyeball the diff
into your own config; after that it's safe to re-run (idempotent).

## How it splits responsibility

- **`npx skills`** ([vercel-labs/skills](https://github.com/vercel-labs/skills)) owns the
  skills: it installs a canonical copy into the store `~/.agents/skills/` and symlinks it
  into every *detected* agent (`~/.claude/skills/`, `~/.codex/skills/`). It never touches
  `CLAUDE.md`/`AGENTS.md`, and it can't see custom profile dirs.
- **`setup-agentic-grimoire`** fills the first gap — it splices the guideline block between
  `<!-- AGENTIC-GRIMOIRE: MANAGED FILE -->` markers in `~/.claude/CLAUDE.md` and
  `~/.codex/AGENTS.md`. A re-run replaces only that block; everything you wrote outside it
  survives.
- **`link-agentic-grimoire-custom`** fills the second — it relative-symlinks root's config
  (`CLAUDE.md`, `RTK.md`, `rules/`, `skills/`, `agents/`, `commands/`) into `~/.claude-personal`
  and `~/.claude-sec`, backing up any real file it replaces, so their config mirrors root instead
  of drifting. Because `skills/` points at root's farm, the custom profiles track the store live.

## Updating

Edit a skill or the guideline blocks here → commit → push → `/sync-agentic-grimoire` inside
Claude Code. It runs `npx skills update --global` (which updates changed skills but, at global
scope, does **not** remove skills deleted upstream) and then prunes those deleted skills — the
gap the CLI leaves. Re-run `/setup-agentic-grimoire` to refresh the managed block (the custom
profiles inherit it through their `CLAUDE.md` symlink). Authors and consumers onboard the same way.

## Uninstall

Run `/uninstall-agentic-grimoire` inside Claude Code — it de-manages root. It strips the
guideline block from `~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md`, and any custom profile that
still holds its own block (preserving everything you wrote outside the markers), then removes
this repo's own skills from the store and every profile. It removes **only** the skills this
repo published; anything you installed from another source is left untouched.

To also **reverse the linking** — so the custom profiles stop mirroring root and get their own
config back — run `/unlink-agentic-grimoire-custom`, the inverse of `/link-agentic-grimoire-custom`.
It removes the config symlinks it created and restores each profile's original from its backups.
A full teardown of a linked setup is `/uninstall-agentic-grimoire` + `/unlink-agentic-grimoire-custom`.

## Repo layout

- `skills/` — the skills, incl. `setup-agentic-grimoire/` (the guideline blocks +
  `splice.sh`), `link-agentic-grimoire-custom/` (`link.sh`),
  `unlink-agentic-grimoire-custom/` (`unlink.sh`), and
  `uninstall-agentic-grimoire/` (`unsplice.sh`).
- `CLAUDE.md` / `AGENTS.md` — this repo's *own* dev guidance (no longer synced anywhere).
- `docs/adr/` — architecture decision records.

