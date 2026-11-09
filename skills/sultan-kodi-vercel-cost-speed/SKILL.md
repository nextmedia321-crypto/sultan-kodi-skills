---
name: sultan-kodi-vercel-cost-speed
description: "Audit a deployed Vercel project for cost and speed, metrics first: collect usage and observability data, gate candidates, investigate only what the data supports, verify, and report ranked recommendations with evidence. Use for bill reduction or performance on Vercel."
---

# Vercel cost and speed review

Observability first. Do not read source files until real production signals point at a route, file or setting.

## Prerequisites
- Recent Vercel CLI with metrics and usage commands, authenticated (the user logs in or uses a token via environment, never typed in commands), app directory linked to the right team/project, Node 20+. Route-level metrics may need the platform's observability add-on; if missing, say what is limited.
- Check the framework (Next.js, SvelteKit, Nuxt best supported; Astro limited; others limited or blocked). If unsupported, stop and ask whether to do a limited platform-level audit.

## Pipeline
1. **Collect:** gather usage and cost by category (bandwidth, function duration, invocations, image optimization, build minutes), top routes by requests/duration/errors, cache hit ratios, project config. Use a fresh run folder every time; do not reuse earlier reports.
2. **Gate:** rank candidates by metric impact. Only items backed by data move on. Ask about audit scope if the project is large.
3. **Investigate:** for each candidate, read only the files tied to that route (and its direct imports). Check the usual causes: uncached or dynamic pages that could be static/ISR, over-fetching, slow or sequential data calls, large function bundles, wrong region, unoptimized or oversized images, chatty middleware, missing cache headers, long function timeouts, preview deployments on every commit, unused features.
4. **Verify:** each recommendation needs a file and line, the metric that justifies it, a version-appropriate fix from official docs, and an expected effect. Remove anything you cannot back up.
5. **Report:** ranked list with estimated savings or speed gain, effort, risk. Group as: recommendations ready; observations from investigation; investigated, no change recommended; not investigated in this run.

## Rules
- Metrics before code; no repo-wide guessing.
- Never print tokens or secrets.
- Make no changes to the project or its settings without explicit approval.
- Be plain in the report: say what costs money and why, in the user's language.

## Output template
`Finding | evidence (usage numbers or build/response times) | estimated saving or speedup | fix | risk`. Rank by estimated monthly saving, then speed gain, and end with the first change to make.

## Example
`Image optimization usage high | 61% of bandwidth from unsized hero images | cut about a third of transfer | serve correctly sized images and cache longer | low risk`.

## Edge cases
- No access to usage data: give a checklist of what to look at and mark estimates as unverified.
- Plan limits you cannot confirm: say so; do not quote prices from memory.
- Never change settings or delete deployments without approval.
