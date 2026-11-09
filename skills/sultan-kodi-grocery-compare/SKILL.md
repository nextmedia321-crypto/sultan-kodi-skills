---
name: sultan-kodi-grocery-compare
description: Compare the price of a shopping list across supermarket chains and say where each item or the whole basket is cheapest. Use when the user gives a grocery list and a country or city.
---

# Grocery price compare

1. Get the list (with quantities) and the location or chains to compare.
2. Look up current prices from the chains' public sites or price-transparency data where they exist. Note the date and source of each price; never invent a price.
3. Match products carefully by brand, size and unit; normalize to price per kg or liter.
4. Output a table: item | chain A | chain B | chain C | cheapest. Then basket totals and the best single-store option versus the best split-store option, including a note when the saving is too small to justify a second trip.
5. State clearly which items could not be found.
