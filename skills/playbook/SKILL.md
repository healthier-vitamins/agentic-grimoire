---
name: playbook
description: Audit changed code against the engineering playbook (established conventions) and flag omissions.
disable-model-invocation: true
---

Every category of code has a **playbook** — the battle-tested standard practice a senior engineer expects. Functional code that ignores its playbook (retry without jitter, write without a transaction, endpoint without authz) passes tests and bites in production. This skill audits a set of changes against the playbook and **voices every departure**, so the convention class can't be silently skipped.

Run the three steps in order. Do not shortcut.

## Step 1 — Resolve scope

Fix exactly **one** concrete review target before reading any convention. Priority:

1. **User named a target** in the invocation (a path, `HEAD`, a SHA, `origin/<branch>`, a `A...B` range) → use it verbatim.
2. **Working-tree changes exist** and nothing was named → audit them:
   ```bash
   git status --porcelain          # staged + unstaged + untracked
   git diff --stat                 # unstaged
   git diff --cached --stat        # staged
   ```
3. **Ambiguous** — clean tree, OR both local edits and an obvious intended commit, OR you cannot tell which the user means → **`AskUserQuestion`**. Offer concrete options: uncommitted changes / last commit `HEAD` / this branch vs `origin/<base>` / a specific SHA. **Never assume a target.**

For a remote ref, fetch before diffing so the base is not stale:
```bash
git fetch origin <base> --quiet
git diff origin/<base>...HEAD --stat
```

**Done when:** one git target is fixed *and* every changed file in it is enumerated (the full list, not a sample). Get the actual diff (`git diff <target>`) — you audit hunks, not filenames.

## Step 2 — Audit against the playbook

Read [`references/conventions.md`](references/conventions.md) — the checklist, grouped by category.

For **every** changed hunk: identify which categories its code touches, then walk **every** convention row in those categories. Each row carries a **Trigger** (when it applies) — fire the row only when the code matches the trigger. This gates false positives: jitter applies to retries against a shared/remote dependency, not a single-shot local call.

**Done when:** every applicable row in every touched category is marked clear or violated against every relevant hunk. The audit is not "find some issues" — it is "account for the whole checklist." A category touched but unchecked is an incomplete audit.

## Step 3 — Report, then fix on confirm

Report each finding:
```
[SEVERITY] (confidence: N/10) path:line — <departure from the playbook>
  Why: <the convention + one-line rationale>
  Fix: <concrete change>
  Ref: <canonical source, if any>
```

- **Severity** — P1 (will bite in prod) / P2 (should fix) / P3 (nit).
- **Confidence** gates display: 9-10 verified by reading the code → show. 7-8 strong → show. 5-6 → show, label "medium confidence". 3-4 → appendix only. 1-2 → only if P1.
- Close with a one-line verdict: clean, or counts by severity.

Then **apply fixes only after the user approves** them. After applying, run the validation that matches the changed scope.
