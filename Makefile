.PHONY: help sync sync-custom sync-sec sync-personal sync-claude sync-codex

help:
	@echo "make sync           - register skills with npx + sync ~/.claude docs/agents + codex"
	@echo "make sync-custom    - mirror store + sync docs/agents into ~/.claude-sec and ~/.claude-personal"
	@echo "make sync-sec       - sync only ~/.claude-sec (docs/agents + skill symlinks)"
	@echo "make sync-personal  - sync only ~/.claude-personal (docs/agents + skill symlinks)"
	@echo "make sync-claude    - sync via Claude Code following SYNC.md"
	@echo "make sync-codex     - sync via Codex following SYNC.md"

# Skill *content* is owned by the `npx skills` CLI: `add ./skills` registers this repo's
# skills into the store (~/.agents/skills) and ~/.claude; `update` refreshes remote skills.
# The python script then handles what npx can't: docs/agents for ~/.claude and codex.
sync:
	npx skills add ./skills --skill '*' --global --agent claude-code --yes
	npx skills update --global --yes
	python3 scripts/sync_agent_docs.py

# Custom profiles the npx CLI can't see. Mirrors the *existing* store into them (run
# `make sync` first if the store needs (re)populating); does not run npx or touch codex.
sync-custom:
	python3 scripts/sync_agent_docs.py --custom

sync-sec:
	python3 scripts/sync_agent_docs.py --only claude-sec

sync-personal:
	python3 scripts/sync_agent_docs.py --only claude-personal

sync-claude:
	claude -p "Read SYNC.md in this repo and follow it to sync the agent docs and skills into my home directory." --permission-mode bypassPermissions

sync-codex:
	codex exec -s danger-full-access "Read SYNC.md in this repo and follow it to sync the agent docs and skills into my home directory."
