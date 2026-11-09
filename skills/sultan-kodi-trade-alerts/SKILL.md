---
name: sultan-kodi-trade-alerts
description: "Set up and check price alert rules (above, below, stop, percent move from previous close, market open) using free delayed quotes, with each alert firing once. Never trades. Use when the user says alert me when, set a stop, price target or watch my stocks."
---

# Trade alerts

Define and evaluate alert rules; tell the user what fired. Nothing is bought or sold.

## Rule types
- **Above / below:** price crosses a level. **Stop:** price falls to a protective level on a holding.
- **Percent move:** change versus the previous close reaches X%.
- **Market open:** a reminder at the US market opening bell (9:30 ET on trading days).
- Each rule fires **once** and then is marked fired, so the user is not spammed; re-arm only on request.

## Market hours
Regular session 9:30-16:00 Eastern on weekdays, closed on US market holidays, early close at 13:00 on the days around some holidays. Always check the current year's official exchange calendar rather than assuming. Outside hours, say prices are from the last close.

## Procedure
1. Parse the request into rules (ticker, type, level, optional note). Confirm back in one line each.
2. Store rules in a small file in the project (for example `trader/alerts.json`) so they persist.
3. To check: fetch one ticker at a time from a free delayed quote source (an official or public chart/CSV endpoint), with a short pause between requests and no more than the user needs. If a source fails, say so; never invent a price.
4. Compare against each rule, report triggered ones with price, time of quote and delay, mark them fired, and write the latest prices to a prices file other skills can reuse.
5. For continuous watching, explain that this needs a scheduled task and ask before setting one up.


**Disclaimer (include in every result):** this is decision support and information, not investment, tax or legal advice. Data can be delayed or wrong; verify with the original source. It never places orders or connects to a broker.
