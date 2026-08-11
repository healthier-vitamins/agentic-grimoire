---
name: keystone
description: Write code as a senior would for the next junior reader — pick a Gang of Four pattern, name in full words and minimal pairs, place files on one axis, keep the flow in one orchestrator file. Use when implementing non-trivial logic or structuring a new module.
---

Write the code for this task as a senior engineer who optimizes for the next junior reader.

## 1. Pick a pattern before inventing structure

Map the problem to an established pattern first. Choose from this catalog rather than inventing bespoke structure, then state the chosen pattern and a one-line reason before writing code.

| Category | Patterns |
|---|---|
| Creational | Factory Method, Abstract Factory, Builder, Prototype, Singleton |
| Structural | Adapter, Bridge, Composite, Decorator, Facade, Flyweight, Proxy |
| Behavioral | Chain of Responsibility, Command, Iterator, Mediator, Memento, Observer, State, Strategy, Template Method, Visitor |
| Architectural | MVC, MVP, MVVM, Repository, CQRS, Event Sourcing, Layered (N-tier), Hexagonal (Ports & Adapters), Clean Architecture |
| Concurrency | Active Object, Monitor, Thread Pool, Producer-Consumer, Scheduler |
| Functional | Functor, Monad, Pipeline, Lens, Trampolining |

If no pattern fits, say so and use the simplest direct structure — do not force a pattern.

## 2. Name for a junior reader

- Names say what the thing holds or does, in full words.
- Ban `tmp`, `data`, `val`, `x`, `mgr`, `obj`, single letters (except loop indices).
- A reader should understand a line without scrolling up or holding hidden state in their head.
- **Minimal pairs.** Counterpart variables along one axis share the whole frame and differ
  only in the axis token: `sql_and_matches` / `sql_or_matches`, never `sql_and_matches` /
  `catch_all_matches`. Name the *set* first (the frame `sql_<op>_matches`), then
  instantiate members; renaming one member renames all its siblings. (Ousterhout,
  *A Philosophy of Software Design* ch. 14 — consistent naming.)
- **No-op word test.** Delete each word from a name; if the meaning inside the current
  scope survives, the word stays deleted. `sql_and_filter_matches` → `sql_and_matches` —
  "filter" is a no-op because every match came from a filter. Corollary: name length
  scales with scope — a tiny loop variable stays short, a module-level export spells
  everything out.

## 3. No opaque expression chains

Every meaningful step gets a named function or named variable. The name carries the intent; the math hides inside the function.

Bad:

```
a = b + c
z = x + a
```

Good:

```
subtotal = add(basePrice, tax)
total    = add(subtotal, shippingFee)
```

## 4. Small, single-purpose functions

Each function does one thing. Code reads top-to-bottom like prose — no clever one-liners, no holding three things in your head at once.

Smallness serves the reader only while the flow stays traceable in one place (§6).
Fragmenting a flow across files to satisfy smallness is the failure mode, not the goal.

## 5. Placement is a claim

Creating a file asserts "this belongs here" — placement is a stated decision, never a
default.

- Before creating a file, state in one line which folder it goes in and why.
- Each tree level sorts by **one axis**. Pick the app's dominant axis and hold it:
  pipeline app → stages (`preprocessing/`, `postprocessing/`), product app → features
  (screaming architecture — Robert Martin), library → capabilities. If the repo already
  has an axis, follow it.
- A folder mixing two axes at the same depth (a `services/` beside a `preprocessing/`) is
  the smell that placement stopped being a claim.

## 6. The flow lives in one file

Every feature owns one orchestrator file that reads top-to-bottom, naming every step in
order (Template Method / Pipeline from the §1 catalog). Tracing the feature means reading
that one file — never chasing pointers across the tree.

Split code out only when the piece earns a *name the orchestrator calls*. Helpers are
**deep modules** (Ousterhout): small interface, deep implementation. A shallow
pass-through file — one that only forwards to another — folds back into its caller.
