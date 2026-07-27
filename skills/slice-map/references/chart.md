# Chart a slice map

## 1. Load the source

Read the complete plan and every source it points to. Inspect only the relevant
codebase areas, domain glossary, and architecture decisions needed to verify its
seams and dependencies.

Build a source inventory with three classes:

- **Behaviour** — assign it to exactly one slice.
- **Constraint** — record it as map-wide or attach it to every affected slice.
- **Validation** — attach it to a slice's verification signal or record it as
  map-wide validation.

Distinguish repository facts from plan assumptions.

**Done when:** every source item appears once in the inventory with its class and
accounting rule.

## 2. Test readiness

State the destination. Identify choices that must be settled before slice
boundaries can be drawn. Hand unresolved decisions to `/wayfinder`; hand
already-settled but scattered requirements to `/to-spec`. Continue with an
implementation-ready plan.

**Done when:** the destination is observable and every slice boundary can be
drawn without inventing a product or architecture decision.

## 3. Cut vertical slices

Partition the behaviours into the smallest slices that each:

- deliver one observable behaviour through every necessary layer;
- can be demonstrated or verified independently;
- fit in one fresh agent context;
- leave the repository in a valid state.

Apply the prerequisite test in `../SKILL.md` to enabling work; fold anything that
fails it into its earliest consumer. Carry every constraint and validation item
from the source inventory into the map's coverage audit.

**Done when:** every source item is accounted for, every behaviour has exactly one
owning slice, every slice has an independent verification signal, and every
prerequisite passes all three statements.

## 4. Wire the critical path

Give slices stable ids, then add an edge only where a concrete gate exists. For
each blocker, record its keyed reason in the dependent row's **Gate** cell:
`S01: <fact>; S02: <fact>`.

Test every edge by asking whether the dependent slice could start and land green
without that blocker; remove the edge when the answer is yes. Detect cycles and
compute the critical path using `../SKILL.md`'s deterministic rule.

Compute the frontier, then choose exactly one slice with `../SKILL.md`'s
recommendation rule.

**Done when:** the graph is acyclic, every blocker has one keyed gate reason,
every open slice is correctly classified as frontier or blocked, the critical
path follows its declared method, and one frontier slice is recommended.

## 5. Render and approve

Write the canonical map with status `Draft`. Show the user the destination,
Mermaid graph, slice index, frontier, and recommendation; keep the coverage audit
in the file. Ask for one approval or correction pass. Apply corrections and mark
the map `Approved` only on confirmation.

**Done when:** an approved canonical map exists, every derived view agrees with
the slice index, and the user can identify the destination, frontier, and next
slice from its low-resolution view.
