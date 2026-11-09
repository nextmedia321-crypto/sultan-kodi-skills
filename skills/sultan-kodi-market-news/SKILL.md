---
name: sultan-kodi-market-news
description: "Brief the user on news and regulatory filings affecting the stocks they hold or watch, only what is new since the last check, newest first, separating confirmed facts from rumors and saying why each item matters. Use for morning briefing or any news on my stocks."
---

# Market news brief

## Procedure
1. Get the watchlist (tickers and holdings) from the user or the saved file.
2. For each ticker collect recent headlines from news sources and recent official filings (for US companies, 8-K events such as earnings, executive changes, deals, restatements, bankruptcy).
3. Show **only what is new since the last check** (keep a small record of items already shown, with date and link) and never repeat an item.
4. Order newest first. For each item: ticker, time, source, one-line summary, a tag (fact from filing / reported by outlet / rumor), and why it may matter to a position (size, direction, timing). Flag items touching large positions first.
5. If nothing new, say so briefly.

Do not predict prices. Quote little; link and summarize in your own words. Cite the source of every item.

**Disclaimer (include in every result):** this is decision support and information, not investment, tax or legal advice. Data can be delayed or wrong; verify with the original source. It never places orders or connects to a broker.
