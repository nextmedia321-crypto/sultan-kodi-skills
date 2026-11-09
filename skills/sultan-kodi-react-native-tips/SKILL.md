---
name: sultan-kodi-react-native-tips
description: "Practical rules for fast, smooth React Native and Expo apps: list performance, animation, navigation, native UI patterns, state, rendering pitfalls, monorepo and configuration. Use when writing or reviewing React Native code."
---

# React Native practical rules

Apply while writing or reviewing React Native / Expo code. Priority runs top to bottom.

## 1. Lists (critical)
- Virtualize long lists (FlashList/FlatList/LegendList), never map inside a ScrollView for big data.
- Keep list items cheap: memoize items, pass stable callback and function references, avoid inline objects/styles in item props, avoid heavy work inside item render, and use item types for mixed lists.
- Use small, correctly sized, cached images in lists. Do not store scroll position in state; use refs or shared values.

## 2. Animation (high)
- Animate GPU-friendly properties (transform, opacity), not layout (width, height, top, margin).
- Use derived values for animations driven by other values; use gesture detectors for press feedback rather than state toggles; keep animation values off the React render path.
- With the React Compiler: destructure functions before use, and treat reanimated shared values with the compiler's rules.

## 3. Navigation (high)
- Use native navigators (native stack, native tabs) for native feel and performance, not JS-drawn imitations.

## 4. UI patterns (high)
- Use the fast image component from your platform (expo-image) with caching and placeholders; build image galleries with the dedicated native gallery approach.
- Prefer native menus and native modals/sheets over custom JS ones; use Pressable instead of legacy touchables; handle safe areas and scroll content insets with the scroll view's own props.
- Measure views with the layout APIs correctly; style through a consistent system; all text must be inside a Text component.

## 5. State (medium)
- Store only the minimum state; derive the rest. Keep a single source of truth. Use a dispatcher/reducer for complex updates, and provide fallbacks so UI never depends on unset state.

## 6. Rendering (medium)
- Never use `&&` with values that can be 0 or an empty string (renders text and can crash); use a ternary or boolean. Hoist expensive objects (like Intl formatters) out of render.

## 7. Monorepo (medium)
- Install native dependencies in the app package that uses them; keep one version of each dependency across the repo.

## 8. Configuration (low)
- Configure custom fonts through the config plugin at build time instead of loading them at runtime; keep shared design-system components in a dedicated folder with clean imports.

Report each issue as `file:line - rule - fix`. Test on a real device or a release build; dev mode performance is not representative.
