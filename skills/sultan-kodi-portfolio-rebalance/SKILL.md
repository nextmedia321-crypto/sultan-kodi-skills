---
name: sultan-kodi-portfolio-rebalance
description: Check a portfolio against its target allocation and propose rebalancing steps with tax and cost awareness. Use when positions have drifted.
---

# Portfolio rebalance

1. Input: holdings with values and the target weights.
2. Compute drift per position and asset class; flag anything beyond a tolerance band (default 5 percentage points).
3. Propose the minimum trades to return to target, preferring new contributions over selling, and note possible taxable events and fees.
4. Show the portfolio before and after as a table.
Decision-support only: not financial advice. State assumptions, show sources and dates for data, and never execute trades.
