---
name: sultan-kodi-react-components
description: Guidance for structuring React components so they stay easy to change: composition over props explosion, compound components, clear state ownership. Use when designing or refactoring component APIs.
---

# React component composition

- Prefer composition: pass children or slots instead of adding boolean props for every variant.
- When a component needs more than about five props that change its layout, split it into smaller parts that share context (a compound component).
- Keep state as low as possible and lift it only when two siblings need it. Derive values instead of storing them.
- Make the common case short and the rare case possible.
- Name by role, not look (`Alert`, not `RedBox`).
- Write a tiny usage example for each new component API before implementing it; if the example is awkward, the API is wrong.
When refactoring, change one component at a time with tests or a visual check in between.
