---
name: sultan-kodi-broker-prep
description: "Prepare a trading plan and pre-trade checklist from proposed orders: a plain ticket per order, limits to verify, and what to confirm in the broker app. It never connects to a broker and never places orders. Use before the user trades themselves."
---

# Broker prep (no execution)

This skill prepares. The user places any order by themselves in their own broker. Do not connect to brokers, handle API keys, or send orders in any form.

## Procedure
1. Take the proposed orders (from the budget, rebalance or the user): ticker, side, quantity or amount, order type, limit price, time in force.
2. Write a plain ticket for each order in readable words, and a one-line rationale tied to the plan.
3. Run the checklist per order: ticker and exchange correct; market or limit (prefer limit, say why); price still near the plan; size within the user's own limits (per-position cap, cash buffer); account type (cash or margin) and settlement; no duplicate of an order already open; fractional shares supported; tax lot or wash-sale considerations flagged for the user's tax review; market hours and liquidity.
4. List "what could go wrong" per order (gaps at the open, partial fills, news pending, earnings date).
5. Output a single checklist the user can tick in their broker app, ordered sells before buys, and a reminder to review each order screen before confirming. If the user asks you to place the orders, decline and explain they do it themselves.


**Disclaimer (include in every result):** this is decision support and information, not investment, tax or legal advice. Data can be delayed or wrong; verify with the original source. It never places orders or connects to a broker.
