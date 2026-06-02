---
name: keystone
description: Write code using a Gang of Four design pattern and naming a junior can read at a glance. Use when implementing non-trivial logic, structuring a new module, or when readability and pattern fit matter.
---

Write the code for this task as a senior engineer who optimizes for the next junior reader.

## 1. Pick a pattern before inventing structure

Map the problem to an established pattern first. Do not guess or invent bespoke structure — choose from this catalog, then state the chosen pattern and a one-line reason before writing code.

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
