---
name: sultan-kodi-react-performance
description: "Find and fix what makes a React or Next.js app slow, ordered by impact: waterfalls, bundle size, server work, client data fetching, re-renders, rendering cost, JavaScript hot paths. Measure before and after. Use when an app is slow or before shipping."
---

# React and Next.js performance

Measure first (build output sizes, Lighthouse/web-vitals, React Profiler, network panel). Work the categories in order of impact and report before/after numbers; revert changes that do not help.

## 1. Eliminate waterfalls (critical)
- Start independent requests together (`Promise.all`); do not await in sequence what does not depend on each other.
- Defer an `await` until the branch that needs it; check cheap conditions before awaiting expensive work.
- Start a promise early, await it late; model true dependencies explicitly so only dependent work waits.
- Use Suspense boundaries so shell UI streams while slow data loads; avoid blocking whole routes on one query. In API routes, start work immediately and await later.

## 2. Bundle size (critical)
- Import from the specific module, not from barrel files that pull in a whole library.
- Load heavy or rarely used components with dynamic import; load code only when a condition or feature flag is true.
- Defer third-party scripts (analytics, chat) until after hydration; preload on user intent (hover, focus) for likely next screens.
- Keep dynamic import paths statically analyzable so the bundler can split them.

## 3. Server-side (high)
- Authenticate and authorize inside every server action, as if it were a public endpoint.
- Cache per-request work (React `cache`) and cross-request work (LRU or framework cache) deliberately; hoist static I/O (fonts, config, assets) to module scope.
- Fetch in parallel, including nested components; restructure so children do not wait on parents unnecessarily.
- Minimize what crosses the server/client boundary: serialize only needed fields; do not pass the same data twice.
- Do not keep mutable shared module state on the server (it leaks between requests). Run non-blocking work (logging, analytics) after the response.

## 4. Client data fetching (medium-high)
- Deduplicate requests with a data library (SWR/React Query); share listeners instead of adding one per component; use passive event listeners for scroll/touch; version and validate localStorage data.

## 5. Re-renders (medium)
- Derive values during render instead of syncing them with effects and state; compute from props/state directly.
- Use functional state updates and lazy initial state; keep effect dependencies primitive and minimal; split hooks that mix unrelated concerns.
- Do not define components inside components; hoist constant props and default values; memoize only proven hot spots and keep memo comparisons cheap.
- Put interaction logic in event handlers, not effects; use transitions or deferred values for non-urgent updates; keep fast-changing values in refs when they need no render; read state (like URL params) lazily, only where used.

## 6. Rendering (medium)
- Hoist static JSX; avoid `&&` with values that can be 0 or empty string (use explicit ternaries); use `content-visibility` for long off-screen sections; prevent hydration flicker for client-only values with an inline script or deliberate suppression; use resource hints (preconnect, preload) for critical origins; put scripts as defer/async; keep SVG precision low and animate wrappers, not the SVG internals; use the Activity/hide pattern to preserve state of hidden UI where available; show loading with transitions rather than manual flags.

## 7. JavaScript hot paths (low-medium)
- Use Map/Set for lookups, build index maps instead of repeated `find`; cache repeated property reads, function results and storage reads inside loops; combine multiple passes into one; exit early; `flatMap` over map+filter; hoist regular expressions; check lengths before expensive comparisons; use a loop instead of sort for min/max; use immutable sort variants; batch DOM/CSS writes; use idle callbacks for non-urgent work.

## 8. Advanced
- Initialize app-wide state once; store latest callbacks in refs; use effect-event patterns so effects do not re-run for non-reactive values.

Images and fonts: correct sizes, modern formats, priority only for the hero, font-display swap. Layout shift: reserve space for media and embeds.

## Output template
`Finding | evidence (measurement or code reference) | priority | fix | before/after number`. Always list the measurement method used so the user can repeat it.

## Example
Finding: three sequential awaits in a server component. Fix: start them in parallel. Evidence: request trace 1.2 s -> 0.5 s after the change.

## Edge cases
- No measurement available: label results as "static review, not measured".
- Premature optimization: skip low-impact items when a critical one is open.
- Never remove accessibility or correctness behavior in the name of speed.
