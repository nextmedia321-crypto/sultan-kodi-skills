---
name: sultan-kodi-stock-screener
description: "Screen a list of companies against the user's own rules (growth, margins, EPS, P/E, earnings yield, sector or any metric), say which rule each company passes or fails and by how much, and rank those that pass. Use when asked to find or filter stocks."
---

# Stock screener

## Procedure
1. Get the rules in the user's words and restate them as exact conditions (metric, comparison, threshold), for example revenue growth > 15%, operating margin > 20%, P/E < 30. Ask if a metric is ambiguous.
2. Get the metrics: from the stock-analyst output or a file the user provides (CSV or JSON). Never fill gaps with invented values; a company with a missing metric is shown as "missing" and not passed.
3. Evaluate every company against every rule. For each company list each rule as pass or fail with the actual value and the margin (how far above or below).
4. Rank companies that pass all rules (default: by the metric the user cares most about, or by the average margin of safety); show near-misses (failing one rule narrowly) separately.
5. Output a shortlist table plus a failures table with reasons. Include the data date for each metric.

Say clearly that passing a screen is not a recommendation: it only means the numbers met the rules.

**Disclaimer (include in every result):** this is decision support and information, not investment, tax or legal advice. Data can be delayed or wrong; verify with the original source. It never places orders or connects to a broker.
