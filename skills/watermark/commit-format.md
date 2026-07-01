# watermark — commit format

Conventional Commits, terse and exact. Same message discipline as `caveman-commit`, with one deliberate exception: watermark **requires** the co-author trailer below (caveman-commit forbids AI attribution; watermark overrides that here).

## Subject line

- `<type>(<scope>): <imperative summary>` — `<scope>` optional
- Types: `feat`, `fix`, `refactor`, `perf`, `docs`, `test`, `chore`, `build`, `ci`, `style`, `revert`
- Imperative mood: "add", "fix", "remove" — not "added", "adds", "adding"
- ≤50 chars when possible, hard cap 72; no trailing period
- Match project convention for capitalization after the colon

## Body (always include one)

- Every commit gets a body — explain the non-obvious *why* behind the change
- Call out breaking changes, migration notes, and linked issues here too
- Wrap at 72 chars; bullets `-` not `*`
- Never write "this commit does X", "I", "we", "now" — the diff says what. Why over what.

## Required trailer

Every watermark commit carries exactly one co-author trailer, written for whichever assistant is running the skill:

- Under Claude Code: `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`
- Under Codex: `Co-Authored-By: Codex <noreply@openai.com>`

Never add a `Claude-Session` line, the session id/URL, or the user's personal name/email to the message. The co-author trailer is the assistant's `noreply` address only (see the Privacy invariant in `SKILL.md`).

## Commit command

Commit normally — use the user's own git config for author identity and signing (nothing overridden, nothing disabled):

```sh
git commit \
  -m "<subject>" \
  -m "<body>" \
  -m "Co-Authored-By: <assistant co-author from above>"
```

The `%an`/`%ae` author fields and any GPG signature come from the user's normal git config — that is expected. The only privacy rule lives in the message text: no session id/URL, no personal name/email in the subject, body, or trailers beyond the `noreply` co-author line.
