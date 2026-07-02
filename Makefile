.PHONY: help sync sync-sec sync-personal sync-claude sync-codex

help:
	@echo "make sync           - sync all targets directly (runs scripts/sync_agent_docs.py)"
	@echo "make sync-sec       - sync only ~/.claude-sec"
	@echo "make sync-personal  - sync only ~/.claude-personal"
	@echo "make sync-claude    - sync via Claude Code following SYNC.md"
	@echo "make sync-codex     - sync via Codex following SYNC.md"

sync:
	python3 scripts/sync_agent_docs.py

sync-sec:
	python3 scripts/sync_agent_docs.py --only claude-sec

sync-personal:
	python3 scripts/sync_agent_docs.py --only claude-personal

sync-claude:
	claude -p "Read SYNC.md in this repo and follow it to sync the agent docs and skills into my home directory." --permission-mode bypassPermissions

sync-codex:
	codex exec -s danger-full-access "Read SYNC.md in this repo and follow it to sync the agent docs and skills into my home directory."
