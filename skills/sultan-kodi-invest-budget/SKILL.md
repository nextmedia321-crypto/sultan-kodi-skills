---
name: sultan-kodi-invest-budget
description: "Size positions to a budget: keep a cash buffer, cap any one stock (excess redistributed), drop slices under a minimum order, round so the money is used, and support fractional or whole shares. Produces proposed orders only. Use when the user says how much of each should I buy."
---

# Investment budget

Turn a total amount and target weights into proposed amounts per position. Nothing is placed.

## Inputs
Total budget; target weights or a list of tickers (equal weight if none); cash buffer percent (default 5-10%); maximum per-stock percent; minimum order size; whole shares or fractional; current prices (with date).

## Algorithm
1. Reserve the cash buffer first; the rest is the investable amount.
2. Compute raw amounts from the weights.
3. Apply the per-stock cap: any excess above the cap is shared out among the others in proportion to their weights; repeat until no one exceeds the cap (state if the cap makes the plan impossible).
4. Drop slices below the minimum order and redistribute their money; say which were dropped.
5. Convert to shares: for whole shares, round down and then use leftover cash on the position furthest below its target; for fractional, round amounts to cents.
6. Check totals: spent plus buffer equals the budget, and nothing exceeds a cap.
7. Output a table (ticker, weight, amount, shares, price and its date) and write proposed orders to a file for later checks. Label them "proposed".

State all assumptions and rounding choices. If prices are missing, ask or fetch them; never guess.

**Disclaimer (include in every result):** this is decision support and information, not investment, tax or legal advice. Data can be delayed or wrong; verify with the original source. It never places orders or connects to a broker.
