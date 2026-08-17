# Philosophy

Depth behind the rules in `SKILL.md`. Read the section a rule points at; nothing here is
needed on every run.

## Connascence — the full ranking

Meilir Page-Jones, *What Every Programmer Should Know About Object-Oriented Design*.
Two pieces of code are connascent when changing one requires changing the other. The
ranking is by **strength** — how much a reader must know about the far end to be correct
at the near end.

**Static forms** (visible by reading the source), weakest to strongest:

| Form | Two pieces agree on | Example |
|---|---|---|
| Name | what something is called | a caller uses the function's name |
| Type | the type of a thing | both sides expect `Decimal`, not `float` |
| Meaning | what a value signifies | `status = 2` meaning "archived" |
| Position | the order of things | positional arguments, tuple unpacking |
| Algorithm | a shared procedure | both sides implement the same hash |

**Dynamic forms** (only visible at runtime, and strictly worse — a reader cannot find them
by reading):

| Form | Two pieces agree on | Example |
|---|---|---|
| Execution | the order operations run in | `init()` must precede `send()` |
| Timing | how long something takes | a race resolved by a sleep |
| Value | several values changing together | `start` and `end` must stay ordered |
| Identity | referencing the same instance | two handles to one mutable buffer |

Three rules follow, in priority order (Page-Jones's own):

1. **Degree** — minimise how many pieces share the connascence. Three callers agreeing on
   argument order is cheaper to fix than thirty.
2. **Strength** — convert strong forms into weak ones. Connascence of meaning becomes
   connascence of name by introducing an enum. Connascence of position becomes connascence
   of name by using keyword arguments.
3. **Locality** — the stronger the connascence, the closer together it lives. Strong
   connascence inside one function is normal and fine; the same strength spanning two
   packages is the thing that makes code unreadable.

Rule 3 is why co-location, minimal-pair naming, and vertical slices are all the same idea
seen from three angles.

## Cognitive complexity — why length is the wrong metric

G. Ann Campbell, *Cognitive Complexity: A New Way of Measuring Understandability*
(SonarSource, 2018). Cyclomatic complexity counts execution paths, which measures testing
effort rather than reading effort — a `switch` with twenty cases scores terribly and reads
easily.

Cognitive complexity instead charges for what actually costs a reader:

- **+1 for each break in linear flow** — a loop, a conditional, a `catch`, a jump.
- **+1 extra per level of nesting** — the fourth nested `if` costs four, not one.
- **nothing for shorthand** the reader absorbs whole — a null-coalescing operator, an
  early-return guard, a `switch` read as one decision.

The consequence for `SKILL.md` §5: nesting is the enemy, length is not. Twelve named calls
in sequence cost twelve. Four nested conditionals cost ten and hurt more.

## Programming as theory building — why a reader may skip most of a file

Peter Naur, *Programming as Theory Building* (1985). A program's real content is the
**theory** held by the people who wrote it: what the world being modelled is like, why the
code maps onto it, and which changes the design will absorb. Source text and documentation
are shadows of that theory, never the thing itself.

Two consequences:

- Reading code means **rebuilding the author's theory**, not scanning every line. A reader
  who has the theory can predict what an unread function does; a reader without it must
  trace everything. This is why tracing an unfamiliar module is exhausting out of
  proportion to its size.
- A file earns being skipped when its interface, its name, and a test that names its
  behaviour together convey enough theory to predict it. That, not brevity, is what makes
  most of a codebase safely unread.

## Pattern catalog

Map the problem here before inventing structure (`SKILL.md` §9). Naming the pattern is the
point — it hands the reader a prior they already hold.

| Category | Patterns |
|---|---|
| Creational | Factory Method, Abstract Factory, Builder, Prototype, Singleton |
| Structural | Adapter, Bridge, Composite, Decorator, Facade, Flyweight, Proxy |
| Behavioral | Chain of Responsibility, Command, Iterator, Mediator, Memento, Observer, State, Strategy, Template Method, Visitor |
| Architectural | MVC, MVP, MVVM, Repository, CQRS, Event Sourcing, Layered (N-tier), Hexagonal (Ports & Adapters), Clean Architecture |
| Concurrency | Active Object, Monitor, Thread Pool, Producer-Consumer, Scheduler |
| Functional | Functor, Monad, Pipeline, Lens, Trampolining |

## Rejected framings

Considered and not adopted, recorded so they are not re-proposed:

- **A line-count ceiling per file.** Measured against a real pipeline, the most confusing
  file had the *best* deep-module ratio (2 public functions of 21) and would have passed
  any plausible cap; the cap catches file bloat, which was never the reported pain.
  Replaced by the seam test (§10) and visible public surface (§4).
- **A maximum call-graph depth.** An eight-frame chain where every hop answers a different
  question reads fine. Depth only hurts when the hops do not pay, which is already covered
  by deep modules (§3) and SLAP (§5).
- **A mechanical checker wired into the repo's lint gate.** A portable skill cannot depend
  on one repo's build scripts, and a rule that needs a checker to be obeyed is a rule whose
  prose failed. The completion checklist in `SKILL.md` carries the enforcement.
- **Semantic compression** (Muratori) — compress code toward the shape the data implies.
  A defensible philosophy that optimises for the author's leverage rather than the next
  reader's load, so it loses to §0's three questions.
