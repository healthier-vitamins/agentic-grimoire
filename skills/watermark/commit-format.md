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
- Write the *why*; the diff already shows the *what*. Avoid narration: "this commit does X", "I", "we", "now".

## Trailers

Identity, signing, and trailers follow **SKILL.md → Identity**.

## Commit command

Commit normally with:

```sh
git commit \
  -m "<subject>" \
  -m "<body>"
```
