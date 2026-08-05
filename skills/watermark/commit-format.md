# watermark — commit format

Conventional Commits, terse and exact. Match the repository's recent commit style.

## Subject line

- `<type>(<scope>): <imperative summary>` — `<scope>` optional
- Types: `feat`, `fix`, `refactor`, `perf`, `docs`, `test`, `chore`, `build`, `ci`, `style`, `revert`
- Imperative mood: "add", "fix", "remove" — not "added", "adds", "adding"
- ≤50 chars when possible, hard cap 72; no trailing period
- Match project convention for capitalization after the colon

## Body — point form

### When a body earns its place

Write one when the *why* is non-obvious, or the commit carries a breaking change, a
migration note, or a linked issue. A trivial commit (typo, rename, version bump) ships as
a subject line alone.

### Shape

```
<subject>

<one-line why: the takeaway, ≤72 chars>

- <one idea>
- <one idea>
```

- **Lead line.** The reader who stops here still has the point.
- **Bullets.** `-`, one idea each. A bullet that reaches for "and", "so", or "because" is
  two bullets — split it at the conjunction. Cap five bullets, two lines each, wrap 72.
- **Voice.** Active, simple present. Name the actor: "The old path resolved to nothing".
  Keep the articles. Noun clusters of three words or fewer.
- **Preservation.** Every claim, condition, and qualifier from your reasoning survives in
  some bullet. A dropped hedge reads clean while being wrong.
- **Breaking change, migration, or issue link.** Its own bullet, `BREAKING:` prefix where
  it applies.

### The cut

Draft for completeness first, then subtract in a second pass — conciseness is not
reachable on a first draft. Delete whole any bullet that re-says the subject, glosses
("in plain words", "essentially"), hedges ("robust", "may potentially"), or narrates
process ("this commit does X", "I", "we", "now"). Emdashes go; use full stops, commas, or
parentheses.

The floor the cut stops at: the *why*, a breaking change, and any fact that changes how
someone acts on this commit. The diff already carries the *what*.

### Worked example

Prose body, three ideas welded into two sentences:

```
The lockfile lives at ~/.agents/.skill-lock.json, not ~/skills-lock.json.
The old path made the jq query resolve to nothing, so the removal ran
with an empty skill list and silently deleted nothing.
```

Same facts, point form:

```
Wrong lockfile path made uninstall a silent no-op.

- The lockfile is ~/.agents/.skill-lock.json, not ~/skills-lock.json
- The old path made the jq query resolve to nothing
- The removal ran on an empty skill list
- The uninstall deleted nothing
```

## Trailers

Identity, signing, and trailers follow **SKILL.md → Identity**.

## Commit command

Commit normally with:

```sh
git commit \
  -m "<subject>" \
  -m "<body>"
```
