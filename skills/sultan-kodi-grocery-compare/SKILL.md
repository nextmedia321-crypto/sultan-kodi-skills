---
name: sultan-kodi-grocery-compare
description: "Compare a grocery shopping list or receipt across supermarket chains and say where it is cheapest, using real price data. Never invent prices; state what was counted, label results as estimates, and disclose what data leaves the device. Use when the user wants the cheapest store for their basket."
---

# Grocery price compare

Guide the user step by step, plain language, saying what you do before you do it. Run the commands yourself; ask the user only for things only they can do.

## Four iron rules
1. **Never invent a price.** Every price comes from a retailer's published price file or a source the user provided, and each result keeps its source and date. A product not found at every compared store is left out of the totals, and you say so.
2. **Say what is counted.** The headline number includes promotions open to everyone (fixed price, "2 for X"). Club/loyalty prices are shown separately. Coupons, gifts and promotions needing a minimum basket are not counted. Always show the shelf-price gap too.
3. **Privacy transparency.** Before sending a receipt photo or list to any model or service, tell the user exactly what is sent and where. Do not store the receipt outside the user's computer.
4. **Say it is an estimate.** Give the disclaimer with every result: data can be wrong or incomplete, prices at the register may differ, no promise on stock or address.

## Flow
1. **Get the basket:** a receipt photo, a typed list, or a past purchase. Read items with quantities and prices; show the parsed list and let the user fix it.
2. **Find the stores:** ask which chain or branches (and city) they use; use official published price-transparency files where they exist (many countries require large retailers to publish daily price and promotion files per branch).
3. **Match products:** by barcode when possible. Matches by name or by type (fruit, vegetables, eggs by kg) are labeled "equivalent" and never called "the same product". Flag weak matches for review.
4. **Check before showing:**
   - weak matches; branches whose location was not verified (say "about" for distance); how many items were really compared out of the total (always state both numbers, with and without promotions); partial branches (if a partial branch looks cheaper on the same items, say it may be the better branch); stale data (yesterday's file); equivalents.
5. **Final message, in order:** recommended store with full address and distance; whether it is worth it (saving vs trip cost = net; if not worth it, say stay); how many items were compared and what was left out and why; extras if present (closer option, two-stop split only when truly worthwhile, biggest gaps, items that are pricier there); the shopping list for that store with quantities and estimated amounts; the disclaimer.

## Limits to tell the user
Published files are legally required but not perfect; an unreported product will not appear; a file does not prove the item is on the shelf; daily files, not intraday changes; complex promotions are approximated and promotions do not stack.

## Output template
Table: `Item | Chain A | Chain B | Chain C | Cheapest`, then a row for the basket total per chain and one line: "Cheapest basket: X, saves N versus the most expensive." Add the price date and source for each chain.

## Example
Basket of 6 items across two chains: show per-item prices, mark unit-size mismatches (e.g. 1 L vs 1.5 L) with the price per liter, and state that item 4 had no match in chain B instead of guessing.

## Edge cases
- Product not found or different size: show the closest match, label it, and compare per unit.
- Promotions that need a membership or minimum basket: list them separately from shelf prices.
- Prices that cannot be retrieved: say so; never estimate.
