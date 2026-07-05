.PHONY: help sync sync-sec sync-personal sync-claude sync-codex

help:
	@echo "make sync           - register skills with npx + sync docs/agents/hooks + mirror store into custom profiles"
	@echo "make sync-sec       - sync only ~/.claude-sec (docs/agents/hooks + skill symlinks)"
	@echo "make sync-personal  - sync only ~/.claude-personal (docs/agents/hooks + skill symlinks)"
	@echo "make sync-claude    - sync via Claude Code following SYNC.md"
	@echo "make sync-codex     - sync via Codex following SYNC.md"

# Skill *content* is owned by the `npx skills` CLI: `add ./skills` registers this repo's
# skills into the store (~/.agents/skills) and ~/.claude; `update` refreshes remote skills.
# The python script then handles what npx can't: docs/agents/hooks, and mirroring the store
# into the custom ~/.claude-sec / ~/.claude-personal profiles as symlinks.
sync:
	npx skills add ./skills --skill '*' --global --agent claude-code --yes
	npx skills update --global --yes
	python3 scripts/sync_agent_docs.py

sync-sec:
	python3 scripts/sync_agent_docs.py --only claude-sec

sync-personal:
	python3 scripts/sync_agent_docs.py --only claude-personal

sync-claude:
	claude -p "Read SYNC.md in this repo and follow it to sync the agent docs and skills into my home directory." --permission-mode bypassPermissions

sync-codex:
	codex exec -s danger-full-access "Read SYNC.md in this repo and follow it to sync the agent docs and skills into my home directory."
