---
name: sultan-kodi-risk-review
description: "Review a portfolio or proposed orders against risk limits: concentration, sector overlap, correlation, blocked tickers, order size, cash buffer, margin, shorts, options and crypto, duplicates and daily limits, with PASS or BLOCK and a reason per item. Use before any trade."
---

# Risk review

Check before anything reaches a broker. Report PASS or BLOCK per order with the reason, and a portfolio summary.

## Order checks
Blocked tickers; maximum order size; minimum order size; maximum position percent after the fill; cash buffer kept; margin use; short selling; options and crypto (off unless the user allowed them); malformed orders (missing fields, impossible quantities); duplicates; daily order count limit.

## Portfolio checks
- **Concentration:** top positions and top-3 share; sector and country exposure.
- **Correlation/overlap:** holdings that tend to move together (same sector, same driver, funds that hold the same stocks).
- **Scenarios:** a simple stress (for example market down 20%, sector down 30%, one position down 50%) with the portfolio impact in percent and currency.
- **Liquidity and event risk:** small caps, earnings dates, pending news.

## Output
Verdict table (order, PASS/BLOCK, reason), portfolio risk summary with the 3 biggest risks, and suggested adjustments. If the user's limits are not known, ask for them or state the defaults you assumed. Any BLOCK stays blocked until the user changes the limit explicitly.

**Disclaimer (include in every result):** this is decision support and information, not investment, tax or legal advice. Data can be delayed or wrong; verify with the original source. It never places orders or connects to a broker.
