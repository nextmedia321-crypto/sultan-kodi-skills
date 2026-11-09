---
name: sultan-kodi-portfolio-rebalance
description: "Check portfolio drift from target weights and propose rebalancing trades: value holdings at current prices, trade only positions outside a band, keep the cash buffer and caps, skip tiny trades, list sells before buys. Proposals only. Use when the portfolio has drifted or new money was added."
---

# Portfolio rebalance

## Procedure
1. Gather holdings (shares), target weights, current prices (with date), cash, and the user's rules: drift band (default 5 percentage points), cash buffer, per-stock cap, minimum trade size.
2. Value each holding; compute current weight and drift = current minus target in percentage points.
3. Only positions outside the band are traded. If none are, say the portfolio is within tolerance.
4. Compute the trades that bring those positions back to target, keeping the cash buffer and per-stock cap; skip trades under the minimum; use new cash first to fix underweights before selling (it avoids taxes).
5. List sells before buys, with amounts and shares, and a post-trade weight table.
6. Flag tax consequences of sells (short vs long term, wash sales) for the user's tax review; do not compute tax here unless asked.
7. Save proposals to a file labeled "proposed"; nothing is executed.

Explain in plain words why each trade is proposed.

**Disclaimer (include in every result):** this is decision support and information, not investment, tax or legal advice. Data can be delayed or wrong; verify with the original source. It never places orders or connects to a broker.
