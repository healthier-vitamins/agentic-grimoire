# watermark — commit format

Conventional Commits, terse and exact. Match the repository's recent commit style.

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

## Trailers

Claude's default `Co-Authored-By: Claude` trailer is expected — leave it. Do not fabricate session id/URL trailers or add the user's personal name/email.

## Commit command

Commit normally — use the user's own git config for author identity and signing (nothing overridden, nothing disabled):

```sh
git commit \
  -m "<subject>" \
  -m "<body>"
```

Identity, GPG signing, and the `Co-Authored-By` trailer all come from the user's normal git config and default setup — nothing overridden (see **Trailers** above).
