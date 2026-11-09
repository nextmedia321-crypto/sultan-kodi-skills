---
name: sultan-kodi-react-performance
description: Performance checklist and fixes for React and Next.js apps: bundle size, rendering, data fetching, images. Use when an app feels slow or before shipping.
---

# React and Next.js performance

Measure first: build output sizes, Lighthouse or web-vitals, React Profiler if available.

Then work the list in order of impact:
1. Ship less JavaScript: dynamic import heavy components, drop unused libraries, avoid importing whole utility packages.
2. Server first: render on the server where possible, keep client components small and at the leaves.
3. Data: fetch in parallel, avoid waterfalls, cache and revalidate deliberately.
4. Rendering: stable keys, memoize only proven hot spots, avoid creating objects in props every render, virtualize long lists.
5. Images and fonts: correct sizes, modern formats, priority only for the hero, font display swap.
6. Layout shift: reserve space for media and embeds.

Report before and after numbers for every change; revert changes that do not help.
