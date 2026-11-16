---
name: review-all
description: Run code-review, ponytail-review and (when the diff crosses a trust boundary) security-review on one diff, in one command.
argument-hint: "[fixed point, default: the default branch]"
disable-model-invocation: true
---

Run the review skills below on one shared diff and report each one's findings. This is review only. Leave the code untouched.

## 1. Pin the diff

- Fixed point: the argument, else the default branch (`main`).
- Diff command: `git diff $(git merge-base <fixed point> HEAD)`. It compares the merge-base to the working tree, so uncommitted work counts. Pass this exact command to every reviewer in place of its own default.
- Spec: the repo's plan file (`PLAN.md`, or the spec the commits name), if one exists.

**Done when:** the fixed point resolves, the diff is non-empty, and you hold the diff command, `git diff --stat` and the spec path.

## 2. Run the reviewers

Invoke each with the Skill tool, one after another, giving each the diff command:

1. `code-review`: pass the fixed point and the spec path.
2. `ponytail:ponytail-review`.
3. `security-review`: only when the diff touches a trust boundary: auth or sign-in, secrets or tokens, permissions or tool gates, or input from outside (web pages, chat messages, HTTP requests, tool results, files the user uploads). Otherwise record "skipped: no trust boundary in the diff" and the files you checked.

**Done when:** every reviewer has returned a report or a recorded skip.

## 3. Report

One `##` heading per reviewer, its findings as it gave them. Keep the reviewers separate: a finding two reviewers raised stays under both, marked "(also in X)". End with one line per reviewer naming its worst finding, then the offer: "Apply the fixes? I'll use `receiving-code-review` if it is installed."
