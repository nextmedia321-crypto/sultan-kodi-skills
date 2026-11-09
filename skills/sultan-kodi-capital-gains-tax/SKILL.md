---
name: sultan-kodi-capital-gains-tax
description: "Estimate capital gains tax and organize trade records: match sales to lots, compute gain or loss, short versus long term, wash-sale flags and loss harvesting ideas, for the user's tax professional to confirm. Use when asked about tax on stock sales."
---

# Capital gains tax helper

## Procedure
1. Ask for the tax country and year (rules differ greatly) and the user's lot-matching method if known (FIFO, specific lots, average cost). State assumptions explicitly.
2. Collect trades: date, ticker, side, quantity, price, fees, currency. Normalize into one table and flag missing cost basis or currency conversions.
3. Match each sale to its lots, compute proceeds minus cost basis minus fees, and classify short or long term using the holding period for that country.
4. Flag wash-sale-type situations (repurchase around a loss sale) and corporate actions (splits, dividends reinvested) that change basis.
5. Total gains and losses by category, apply loss netting and carryover as the country's rules allow, and estimate tax using the rates the user provides or official published rates (cite the source and year).
6. Optionally list loss-harvesting or timing ideas as questions for the tax advisor, with trade-offs.
7. Output a clean records table the accountant can use, and a short summary.

Always state: this is an estimate from the data given; a licensed tax advisor must confirm before filing. Do not give personalized tax advice or file anything.

**Disclaimer (include in every result):** this is decision support and information, not investment, tax or legal advice. Data can be delayed or wrong; verify with the original source. It never places orders or connects to a broker.
