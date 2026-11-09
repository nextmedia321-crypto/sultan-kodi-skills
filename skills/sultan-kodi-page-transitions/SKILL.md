---
name: sultan-kodi-page-transitions
description: "Add smooth, native-feeling page and element transitions in React with the View Transition API: shared elements, Suspense reveals, list reorders, enter/exit and route changes, with graceful fallback. Use when asked to animate navigation or UI state changes."
---

# Page transitions with View Transitions

The browser's native view transition animates between two UI states. In React you declare **what** with a `<ViewTransition>` wrapper, trigger **when** with a transition (`startTransition`, `useDeferredValue`, Suspense), and control **how** with CSS. Browsers without support skip the animation and the app still works.

## When to animate
Every transition must communicate a relationship. If you cannot say what it communicates, do not add it. Apply all patterns that fit, in this order:
1. **Shared element** (same `name` on both sides): "same thing, going deeper" (list to detail).
2. **Suspense reveal**: "data loaded" (fallback to content).
3. **List identity** (a stable key per item): "same items, new arrangement" (reorder, filter).
4. **State change** (enter/exit): "something appeared or went away".
5. **Route change**: "going to a new place".
Style guide: directional slides only for hierarchical navigation (list to detail) and ordered sequences (next/previous); tab-to-tab uses a fade or none; silent background refresh uses no animation.

## Availability
- Next.js App Router already bundles the needed React canary: do not install it separately.
- Without Next.js you need React canary builds until the component reaches stable.
- Support: Chromium 125+, Firefox 144+, Safari 18.2+. Always keep a no-animation fallback.

## Implementation workflow
1. Audit: list the app's routes, lists, detail views, Suspense boundaries and state toggles that already change visually.
2. Wrap the element that should animate with `<ViewTransition>`; put it at the top of what is being added or removed, because a transition only fires if it sits directly above the DOM change (do not hide it inside deeper wrappers).
3. Trigger updates inside a transition so React can capture before/after states.
4. Pick animation with CSS view-transition pseudo-elements (`::view-transition-old`, `::view-transition-new`, `::view-transition-group`) via classes passed to the component; use transition types (for example forward vs back) to choose direction; handle router back and the browser back button explicitly.
5. Shared elements need the same unique `name` on both sides and must be ready (mounted) when the transition captures.
6. When several transitions coexist, set `default="none"` deliberately on parents so only the intended ones animate; avoid nesting a transition that you expect to animate independently inside another.
7. Force a re-enter with a changing `key` when content swaps.

## Accessibility and quality
- Respect `prefers-reduced-motion`: disable or shorten transitions.
- Keep durations short (about 150-400ms) and never block interaction.
- Test back/forward, fast repeated clicks, slow network and an unsupported browser.

## Output template
Deliver: the code change, a one-paragraph note on which transitions were added and why, the browsers where it animates, and the fallback behavior elsewhere.

## Example
List-to-detail navigation: shared element named by id, 250 ms ease-out, disabled when the user prefers reduced motion; browsers without support simply navigate instantly.

## Edge cases
- Very long or heavy pages: keep the animation under 300 ms or skip it.
- Reduced-motion users: no movement, optional quick fade only.
- If a transition causes layout shift or flicker on a slow device, remove it rather than tune it.
