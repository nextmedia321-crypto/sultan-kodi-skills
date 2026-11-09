---
name: sultan-kodi-investor-tracker
description: "Summarize what a well-known investor or fund holds from its public regulatory filings (13F and related), with positions, share of portfolio, and what was bought, added, trimmed or sold since last quarter. Use when asked what a fund owns or to copy a portfolio's weights."
---

# Investor tracker

Use public filings only (for US funds, the quarterly 13F-HR holdings report on SEC EDGAR, and insider Form 4 if requested). 

## Procedure
1. Identify the filer (name or CIK) and fetch the latest and the previous 13F.
2. Match each CUSIP to a ticker; flag unmatched or ambiguous ones.
3. Table: position, shares, value, share of the reported portfolio; changes since last quarter: new, added, trimmed, sold out.
4. If asked to copy the portfolio: take the top N positions, re-normalize weights, and save them as target weights for the budget skill.

## Always say
- 13F data is delayed up to 45 days after quarter end, shows only long US-listed positions (no shorts, most bonds or foreign holdings), and tells nothing about the price paid or later trades. Copying a stale filing may differ greatly from the fund's current positions.
- Do not imply the investor endorses anything or that the filing predicts returns.

**Disclaimer (include in every result):** this is decision support and information, not investment, tax or legal advice. Data can be delayed or wrong; verify with the original source. It never places orders or connects to a broker.
