---
name: keystone-react
description: Write React for the next junior reader, who should know from one file where they are in the tree and what it owns. Use when building or refactoring React components, pages, or features.
---

## 0. Keystone still applies

Every rule from `keystone` holds — its three questions (change amplification, cognitive
load, unknown unknowns), connascence, locality of behaviour, the keystone file, newspaper
order, and the seam test. This file adds the React layer.

## 1. The tier ladder

Name every component `<Domain><Tier>`. The suffix tells the reader how deep in the tree
they are. Outermost to innermost:

```
UserSettingsPage           route entry — data fetch + providers
  UserSettingsOrchestrator state orchestration, no markup of its own
    ProfileSection         a titled division of the page
      AvatarPanel          a grouping inside a section, no chrome of its own
        AvatarCard         a bordered unit that still makes sense lifted out
          AvatarField      a single control
```

`Page → Orchestrator → Section → Panel → Card → Field`

Each tier owns one responsibility, and the ladder runs one way: a `Card` sits inside a
`Section`, never around one. Skip any tier the feature does not need.

The entry component carries `Page`, and that suffix is the "main" marker. The
`Page`/`Orchestrator` tier **is** the feature's keystone file (`keystone` §3): its render
reads top-to-bottom naming every child in order, so tracing the feature means reading that
one file.

Vocabulary: `Container` was the earlier name for the `Orchestrator` tier and is retired —
container/presentational carries a strong prior that its own author, Dan Abramov,
publicly retracted, and the prior fights the tier's actual job.

## 2. Colocate, then decompose

**Colocation** (Kent C. Dodds): code lives as close to where it is relevant as possible.
Styles, hooks, types, tests, and handlers for one component sit beside that component, and
move up the tree only when a second consumer appears. This is `keystone` §1 — the stronger
the coupling, the closer it lives — applied to a feature folder.

A `return` that needs comments to separate its blocks is describing components it has not
made yet:

```tsx
return (
  <UserSettingsOrchestrator>
    <ProfileSection />
    <SecuritySection />
  </UserSettingsOrchestrator>
);
```

One component per file, named for what it renders. Where a JSX block would earn a
`{/* comment */}`, the name of a component says it better.

A component earns its own file when its parent renders it by name and there is real markup
behind a small props interface — a **deep module**. **Props are the interface**: few props
with rich markup behind them is deep; many props with thin markup is shallow, and shallow
components cost the reader a file for nothing. Shallow ones fold back into the parent.

**Compound components** (Florence) are the pattern the ladder is reaching for whenever
children need the parent's state — `<Tabs><Tabs.List /><Tabs.Panel /></Tabs>` — because
the relationship shows in the markup instead of in props.

## 3. The visible surface of a file

TypeScript already marks the public surface: `export` is the door, and everything
unexported is furniture. Export the component the parent renders; keep its helpers, its
sub-hooks, and its constants unexported in the same file.

Newspaper order applies inside a file too — the exported component first, its local
helpers and hooks below it.

Size is not a rule. When a file feels too large, apply `keystone` §10: to change one half,
must the reader read the other?

## 4. Context over prop-drilling

- Lift state as far as necessary and no further (React docs). Reach for a Context Provider
  when a value crosses two or more levels or feeds siblings.
- Wrap the provider around the subtree that consumes it, so the data's real scope is
  visible and the rest of the app does not re-render.
- Keep the provider and its hook in one file. Consumers import the hook, which is a Facade
  that throws when used outside the provider and so guarantees a non-null value.

## 5. Handler maps

Loose `handleRoleChange`, `handleDivisionChange`… scatter one intent across a file.
Collect them into one keyed object per event family, with a JSDoc per key. The object is
named for the event, the key mirrors the field or action — the minimal-pair rule
(`keystone` §7) applied to keys. This is a dispatch map (Strategy): the handler is selected
by key.

```tsx
/**
 * On change handlers
 */
const onChangeHandlers = {
  /**
   * Role — clear dependent fields
   */
  role: () => {
    form.setFieldValue("division", undefined);
    updateDivisionAccess([], undefined);
  },
  /**
   * Division — reset access for the new division
   */
  division: (value: DivisionCode) => {
    if (selectedRoleHasAllDivisionAccess) return;
    updateDivisionAccess([value], value);
  },
};
```

```tsx
<Select onChange={onChangeHandlers.role} />
<Select onChange={onChangeHandlers.division} />
```

The map trades **locality of behaviour** for a single home: the reader at the `<Select>`
must look elsewhere to learn what changing it does. That trade pays from about **four
handlers in one family** — below that, an inline handler beside the element it serves reads
better. Same shape for `onSubmitHandlers`, `onClickHandlers`.

## 6. CSS is component-scoped by default

- Styles sit beside the component and are imported only there: `AvatarCard.module.css`
  beside `AvatarCard.tsx`, or a styled-component in-file.
- The global stylesheet holds app-wide concerns only — resets, design tokens, base
  typography — in one documented place.
- A style affecting one component belongs in that component's sheet.

## 7. Feature folder

```
UserSettings/
  UserSettingsPage.tsx            entry — fetch + providers
  UserSettingsOrchestrator.tsx    state orchestration
  UserSettingsContext.tsx         provider + useUserSettings()
  ProfileSection.tsx
  ProfileSection.module.css
  AvatarCard.tsx
  AvatarCard.module.css
  useAvatarUpload.ts              extracted hook
```

A reader lands in this folder and the filenames alone tell the whole story.

## Done when

Every one of these holds for the components just written:

- Every component is named `<Domain><Tier>` and its tier sits below its parent's on the
  ladder.
- Every file exports the component its parent renders, and nothing else.
- Every file is in newspaper order — the exported component above its local helpers.
- Every component either has real markup behind a small props interface, or has folded back
  into its parent.
- Every provider wraps only its consuming subtree, and its hook guarantees the value.
- Every handler map has four or more handlers; smaller families are inline.
- Every style affecting one component lives beside that component.
