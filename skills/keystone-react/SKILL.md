---
name: keystone-react
description: Write React as a senior would for the next junior reader — GoF patterns, decomposed components, context over prop-drilling, grouped handlers, co-located CSS. Use when building or refactoring React components, pages, or features.
---

Write React for the next junior reader. They should open any file and know — without
scrolling — where they are in the tree and what the file is responsible for.

## 0. Keystone still applies

Every rule from `keystone` holds: pick an established (Gang of Four) pattern before
inventing structure, name in full words, no opaque expression chains, small
single-purpose functions. This file adds the React layer on top.

## 1. Component hierarchy & naming

Name every component `<Domain><Tier>`. The tier suffix tells the reader how deep they
are. Outermost → innermost:

```
UserSettingsPage         route entry — data fetch + providers
  UserSettingsContainer  state orchestration, no markup of its own
    ProfileSection       a logical group on the page
      AvatarPanel        a sub-region inside a section
        AvatarCard        a bordered, self-contained unit
          AvatarField     a single control
```

`Page → Container → Section → Panel → Card → Field`

- Each tier owns **one** responsibility.
- Skip tiers you don't need; **never reorder** them. A `Card` never wraps a `Section`.
- The entry component carries the top suffix (`Page`). That suffix **is** the "main"
  marker — no `Main` prefix, no special casing.

## 2. Decompose JSX — no inline walls

A `return` that needs comments to separate its blocks is hiding components.

Bad — wall of inline markup:

```tsx
return (
  <>
    {/* profile: 40 lines of markup */}
    {/* security: 40 lines of markup */}
  </>
);
```

Good — each block is a named component in its own file:

```tsx
return (
  <UserSettingsContainer>
    <ProfileSection />
    <SecuritySection />
  </UserSettingsContainer>
);
```

Rule: one component = one file, named for what it renders. If a JSX block would earn a
`{/* comment */}` to explain it, make it a component instead — the name is the comment.

## 3. File-size ceiling

Hard ceiling: **800–1000 LOC per file.** Crossing it is the signal to split — extract
child components (§2), hooks (`useXxx.ts`), or handler objects (§5) into co-located
files. Size is a smell, not the target: split along responsibility seams, not at an
arbitrary line count.

## 4. Context over prop-drilling

- Reach for a Context Provider when a value crosses **≥2 levels** or feeds siblings.
- **Wrap the provider only around the subtree that consumes it.** Never hoist it to the
  app root "just in case" — that re-renders the world and hides the data's real scope.
- Co-locate the provider and its hook in one file. Consumers import the hook, never call
  `useContext` raw — the hook is a Facade that guarantees the value exists.

```tsx
// UserSettingsContext.tsx
const UserSettingsContext = createContext<UserSettings | null>(null);

export function UserSettingsProvider({ value, children }: Props) {
  return (
    <UserSettingsContext.Provider value={value}>
      {children}
    </UserSettingsContext.Provider>
  );
}

export function useUserSettings(): UserSettings {
  const settings = useContext(UserSettingsContext);
  if (!settings) {
    throw new Error("useUserSettings must be used inside <UserSettingsProvider>");
  }
  return settings;
}
```

## 5. Group event handlers in resolver objects

Loose `handleRoleChange`, `handleDivisionChange`… scatter intent across the file.
Collate them into one keyed object per event type, with a JSDoc per key. Keys mirror the
field or action; each handler stays small (keystone rule 4). This is the Strategy /
lookup-map pattern — the handler is selected by key, not by an `if`/`switch`.

```tsx
/**
 * On change handlers
 */
const onChangeResolvers = {
  /**
   * Role on change — clear dependent fields
   */
  role: () => {
    form.setFieldValue("division", undefined);
    updateDivisionAccess([], undefined);
  },
  /**
   * Division on change — reset access for the new division
   */
  division: (value: DivisionCode) => {
    if (selectedRoleHasAllDivisionAccess) return;
    updateDivisionAccess([value], value);
  }
  // …one key per field/action, each handler small (keystone rule 4)
};
```

Wire it inline at the call site:

```tsx
<Select onChange={onChangeResolvers.role} />
<Select onChange={onChangeResolvers.division} />
```

Same shape for the other event families: `onSubmitResolvers`, `onClickResolvers`. Name
the object by event, name the key by field/action.

## 6. CSS is component-scoped by default

- Co-locate styles next to the component and import them only there:
  `AvatarCard.module.css` beside `AvatarCard.tsx` (or a styled-component in-file).
- Global CSS is reserved for true app-wide concerns — resets, design tokens, base
  typography — in one documented global stylesheet.
- Rule: if a style affects only one component, it must not live in a global sheet.

## 7. Feature folder — how it fits together

```
UserSettings/
  UserSettingsPage.tsx          entry — fetch + providers
  UserSettingsContainer.tsx     state orchestration
  UserSettingsContext.tsx       provider + useUserSettings()
  ProfileSection.tsx
  ProfileSection.module.css
  AvatarCard.tsx
  AvatarCard.module.css
  useAvatarUpload.ts            extracted hook
```

A reader lands in this folder and the filenames alone tell the whole story.
