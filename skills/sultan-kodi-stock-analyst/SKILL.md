---
name: sultan-kodi-stock-analyst
description: "Analyze a company from its reported numbers in official filings: revenue, margins, net income and EPS by quarter versus the same quarter a year earlier, trailing twelve months, valuation and risks. Use when asked how earnings looked or whether revenue is growing."
---

# Stock analyst

Read what the company itself reported, not rumors.

## Sources
Prefer official filings: for US companies the SEC's EDGAR (10-K, 10-Q, the latest earnings 8-K and its press release; structured company facts when available). Cite each number with its filing and period. Never invent figures; if a number is unavailable, say so.

## Steps
1. Resolve the ticker to the company and its filings.
2. Build a quarterly table: revenue, gross margin, operating margin, net margin, net income, diluted EPS; each versus the same quarter last year (year-over-year change), plus the trailing twelve months (sum of the last four quarters).
3. Say what changed in plain words: growth speeding up or slowing, margin expansion or squeeze, one-off items, guidance if stated, share count changes.
4. Valuation context from the user's inputs or a clearly sourced price: price-to-earnings, earnings yield, with the date of the price.
5. Risks: customer or product concentration, debt, cash burn, accounting notes, legal items mentioned in the filings.
6. Save the key metrics to a file (CSV or JSON) in a simple shape so a screener can read them.
7. For several tickers, repeat and add a comparison table.

Separate facts (from filings) from your interpretation, and label interpretation as such.

**Disclaimer (include in every result):** this is decision support and information, not investment, tax or legal advice. Data can be delayed or wrong; verify with the original source. It never places orders or connects to a broker.
