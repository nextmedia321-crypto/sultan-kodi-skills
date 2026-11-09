---
name: sultan-kodi-react-native-tips
description: Practical rules for fast, smooth React Native apps: lists, images, animation, navigation, re-renders. Use when building or tuning a mobile app.
---

# React Native practical rules

- Lists: use FlatList or FlashList, stable keys, fixed item heights when possible, avoid inline functions in renderItem.
- Images: resize server-side, cache, avoid huge bitmaps.
- Animation: run on the native thread (Reanimated), never animate layout props on the JS thread in a loop.
- Re-renders: memoize list items, keep context values stable, split state.
- Navigation: lazy-load screens, keep screens light.
- Always test on a mid-range physical device and in release mode, not just the simulator.
Report the measured frame rate or startup time before and after each change.
