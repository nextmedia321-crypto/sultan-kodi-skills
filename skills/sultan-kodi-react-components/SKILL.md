---
name: sultan-kodi-react-components
description: "Rules for building flexible React components: avoid boolean-prop sprawl, use compound components, lift state to providers, define a generic context interface, prefer children over render props, explicit variants, and React 19 API changes. Use when designing or refactoring component libraries."
---

# React component composition

Use when designing, reviewing or refactoring React components, especially reusable or shared ones.

## 1. Component architecture (high priority)
- **No boolean-prop sprawl.** When a component grows `isX`, `hasY`, `showZ` flags that combine into invalid or confusing states, stop adding flags. Split into composable parts or explicit variants instead.
- **Compound components.** Expose a family (`Card`, `Card.Header`, `Card.Body`) that shares state through context, so callers assemble the UI they need rather than passing a configuration object.

## 2. State management (medium)
- **Lift state up** to a provider when siblings need it; keep UI parts presentational and state-free where possible.
- **Define a generic context interface** (state, actions, meta) so different providers can satisfy the same UI. The UI depends on the interface, not on a particular data source.
- **Decouple state implementation from the UI.** Only the provider knows whether state comes from useState, a reducer, a store or the server; the components just read and call actions.

## 3. Implementation patterns (medium)
- **Prefer children and composition over render props** unless the child truly needs data from the parent at render time.
- **Explicit variant components** (`PrimaryButton`, `DangerButton` or a `variant` union) instead of piles of conditions inside one component.

## 4. React 19 (medium)
- `ref` is a regular prop on function components, so drop `forwardRef` in new code.
- Read context with `use(Context)` (it can be called conditionally), instead of `useContext` where the project targets 19+.
- Only apply these when the project uses React 19; check the installed version first.

## How to use
1. Read the component(s) in question and name the problem (flag explosion, prop drilling, tangled state, wrapper hell).
2. Pick the matching rule above, show a before/after of the smallest change, and keep behavior identical.
3. Do not rewrite working components just to match a pattern; refactor when a real change is painful.

## Output template
For a review: `Issue | file:line | rule (section number) | suggested change` ordered by priority; for new code: the component plus a one-line reason for each composition choice.

## Example
Before: `<Card showHeader showFooter isCompact />`. After: `<Card><Card.Header/><Card.Body/></Card>` with shared state in context; the prop explosion is gone and each part can be tested alone.

## Edge cases
- Small one-off components: do not force composition patterns where a plain component is clearer.
- Legacy class components: leave them unless the user asks for a migration.
- Check the React version before suggesting version-specific APIs.
