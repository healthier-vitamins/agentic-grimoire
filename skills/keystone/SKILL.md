---
name: keystone
description: Write code for the next junior reader instead of for the compiler. Use when implementing non-trivial logic, structuring a module, or judging whether existing code can be read.
---

The reader is the constraint. Ask three questions of every design (Ousterhout,
*A Philosophy of Software Design*):

- **Change amplification** — how many places must change to make one change?
- **Cognitive load** — how much must the reader hold in their head to be correct here?
- **Unknown unknowns** — can the reader tell which code a change might break?

Every rule below serves one of the three. When two rules collide, the one lowering
cognitive load wins.

## 1. Coupling decides distance

**Connascence** (Page-Jones) ranks how strongly two pieces of code know about each other,
weakest to strongest:

`name < type < meaning < position < algorithm`

The rule: **the stronger the connascence, the closer together the code lives.** Two
functions that agree on a name can sit in different packages. Two that agree on the
meaning of a magic value, or on argument order, or on a shared algorithm, belong in the
same file — because a reader changing one must find the other, and only proximity makes
that possible.

Cross-file connascence of meaning or position is what makes tracing exhausting: the
knowledge needed to be correct lives somewhere the reader cannot see. Full ranking,
including the dynamic forms (execution, timing, value, identity), in
[references/philosophy.md](references/philosophy.md).

## 2. Behaviour is obvious from the unit alone

**Locality of behaviour** (Gross): reading one function tells the reader what it does,
without opening another file.

This trades against DRY, and the trade has a direction: **duplicate a small expression
before you extract a shared helper that both callers must open to understand.** Extract
when the shared thing has a name worth learning, not when two lines happen to match.

## 3. The keystone file

Every feature owns one file that holds its flow — the **keystone**, the stone the arch
depends on. It reads top-to-bottom, naming every step in order (Template Method or
Pipeline). Tracing the feature means reading that one file.

**Newspaper order** (Clean Code ch. 5): the public entry sits at the top, its callees
below it, depth increasing downward. A reader landing at line 1 is standing at the door,
and reading downward is descending the call graph.

Where a module-level value must be defined after the functions it references, wrap it in a
function so the ordering survives: `def _route_chain(): return [...]` at the top reads as
the file's table of contents.

Split code out when the piece earns a **name the keystone calls**. Helpers are **deep
modules** (Ousterhout): small interface, deep implementation. A file that only forwards to
another folds back into its caller.

## 4. The public surface is visible on landing

A reader who opens a file must see, without scanning it, which functions are the door and
which are furniture. Mark it with the language's own mechanism — a leading underscore in
Python plus `__all__` at the top; the `export` keyword in TypeScript. Everything one file
uses stays unmarked.

A module's public surface has direct tests. A public function reachable only through
end-to-end tests is unreadable by construction: there is no way to learn what it does
except by tracing it, which is the cost this whole skill exists to remove. (`tdd` owns
how to write them.)

## 5. One level of abstraction per function

**SLAP**: every statement in a function body sits at the same level. A function that
orchestrates four pipeline stages does not also strip a suffix off a string — the reader
cannot tell which lines matter.

This is what "no god functions" means operationally, and it is about nesting and mixed
altitude rather than length (Campbell's **cognitive complexity**, see
[references/philosophy.md](references/philosophy.md)). A 200-line function that is twelve
named calls in sequence reads fine. A 40-line function three levels deep does not.

## 6. Every meaningful step carries a name

A named function or named variable per step; the arithmetic hides inside the name.

```
subtotal = add(base_price, tax)
total    = add(subtotal, shipping_fee)
```

## 7. Names spell out what they hold

- Full words, naming the noun held or the verb performed. Name length scales with scope: a
  loop index stays short, a module-level export spells everything out.
- **Frames and minimal pairs.** Counterpart names along one dimension share the whole
  frame and differ only in the varying token: `sql_and_matches` / `sql_or_matches`. Name
  the frame first (`sql_<op>_matches`), then instantiate its members, so renaming one
  renames all its siblings. (Ousterhout ch. 14, consistent naming.)
- **No-op word test.** Delete each word from the name; if the meaning inside the current
  scope survives, the word stays deleted. `sql_and_filter_matches` → `sql_and_matches`:
  "filter" is a no-op because every match came from a filter.

Vocabulary note: **frame** is the naming dimension (§7); **axis** is the placement
dimension (§8). They are different ideas — keep the words apart.

## 8. Placement is a claim

Creating a file asserts "this belongs here". State in one line which folder it goes in and
why.

- Each tree level sorts by **one axis**. Pick the app's dominant axis and hold it: pipeline
  app → stages (`preprocessing/`), product app → features (screaming architecture, Martin),
  library → capabilities. An existing axis in the repo wins.
- A folder mixing two axes at one depth (a `services/` beside a `preprocessing/`) is the
  smell that placement stopped being a claim.
- A framework's prescribed layout (NestJS modules, Rails MVC, Next.js app router) **is** the
  axis — scaffold with it.
- Layered frameworks resolve to **vertical slices**: top level is features, layers live
  inside each slice. Controller/service is a floor: when logic outgrows the service, grow
  the slice with new named files.
- Orchestration has a canonical home — the **use-case** file inside its slice (Clean
  Architecture's interactors): `partner_merge/merge_partners.usecase.ts`.
- `utilities/` earns its name only when every file in it is domain-free *and* consumed by
  ≥2 slices. One consumer means the code lives in that slice. (Google's Go style guide bans
  grab-bag `util`/`common` packages for the same reason.)

## 9. Pattern before bespoke structure, and the pattern pays rent

Map the problem to an established pattern and state the pattern plus a one-line reason
before writing code. Catalog in [references/philosophy.md](references/philosophy.md). Where
no pattern fits, say so and use the simplest direct structure.

Patterns buy structure with **indirection**, and the reader pays. A pattern that replaces
readable dispatch with runtime dispatch — Chain of Responsibility, Strategy, a handler map
— earns it when there are **three or more variants**, and it stays readable when the
dispatch table is a literal list in the same file, in execution order, with the selecting
condition inline. Two variants read better as an `if`.

## 10. The seam test — is this one feature or two?

When a file feels too large, the question is not its length. It is: **to change A, must I
read B?** If a change to one half never requires reading the other, they are two features
wearing one name, and the fix is a second named file rather than extracted helpers. Git
history settles it — commits touching A that never touch B were never one feature. (Parnas,
*On the Criteria To Be Used in Decomposing Systems into Modules*.)

The cheap confirmation: the name needs an "and". `route_and_merge` is
`decide_merge_route` plus `apply_merge_route`.

Length itself is not a rule here. No line-count ceiling replaces the seam test, because a
600-line file a reader can enter and leave costs less than a 150-line file that hides its
door.

## Done when

Every one of these holds for the code just written:

- Every file's public surface is marked, and its non-public functions are not.
- Every file is in newspaper order — no callee defined above its caller.
- Every name survives the no-op word test, and counterpart names share a frame.
- Every function holds one level of abstraction.
- Every new file's folder was stated as a claim, on the tree's existing axis.
- Every pattern introducing runtime dispatch has ≥3 variants and a literal table.
- Every module with a public surface has a direct test naming its behaviour.
- The seam test was applied to any file that felt too large.
