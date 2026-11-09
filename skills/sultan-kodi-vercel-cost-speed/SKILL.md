---
name: sultan-kodi-vercel-cost-speed
description: Find ways to cut cost and improve speed for a project already running on Vercel: functions, caching, images, build settings. Use when bills or latency rise.
---

# Vercel cost and speed review

1. Gather usage data: function duration and invocations, bandwidth, image optimization counts, build minutes, cache hit rate.
2. Look for: functions that could be static or cached, wrong regions, oversized or unoptimized images, missing cache headers, builds triggered too often, large bundles.
3. Rank recommendations by estimated monthly savings or latency gain, with the specific setting or code change.
4. Apply changes one at a time and measure again. Report before and after.
