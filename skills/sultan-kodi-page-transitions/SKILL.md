---
name: sultan-kodi-page-transitions
description: Add smooth page and element transitions to web apps using the View Transitions API with a safe fallback. Use when the user wants animated navigation.
---

# Page transitions

1. Feature-detect `document.startViewTransition`; fall back to no animation.
2. Wrap the DOM or route update inside the transition callback.
3. Name shared elements with `view-transition-name` (unique per page) so they morph between states.
4. Style `::view-transition-old(...)` and `::view-transition-new(...)` with short durations (150 to 300 ms) and easing that fits the brand.
5. Honor `prefers-reduced-motion` by disabling the animation.
6. Test back/forward navigation and rapid clicking; fix flicker and scroll jumps.
