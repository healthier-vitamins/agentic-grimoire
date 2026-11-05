---
name: chat-id
description: Print the current Claude Code chat's session ID.
disable-model-invocation: true
---

Run:

```sh
printenv CLAUDE_CODE_SESSION_ID
```

Reply with the ID alone, in a code span, so it is easy to copy.

If the variable is unset, say so and stop. The newest transcript in `~/.claude/projects` can belong to another open chat, so it cannot stand in for the ID.
