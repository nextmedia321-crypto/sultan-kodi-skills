---
name: sultan-kodi-codebase-map
description: "Map and untangle a codebase: first a compact navigation map, then (only on request) a root-cause cleanup that removes hidden dependencies, needless coupling, dead weight and special-case code. Use when starting on a large messy repo or when asked for a deep cleanup."
---

# Codebase map and untangle

Two modes. The default is **map only**: safe, no code edits. Use **untangle** only when the user clearly asks for a cleanup or refactor.

## Mode 1 - Map
1. Survey the root files, manifests, entry points, configs, the tests layout and CI. Search instead of opening everything; a "skeleton" view (signatures with bodies stripped) lets a whole repo fit in context.
2. Write `CODEBASE_MAP.md`, roughly 200 lines at most: what the project is for (two sentences); a folder tree with one line per important folder; commands to run, test and build; the main flow of data; key modules and what each owns; external services and the NAMES of environment variables (never values); hazards such as dead code, duplicated logic or hidden coupling; where to begin for typical tasks. Tag anything you could not confirm as "unverified".

## Mode 2 - Untangle
Benefit: a clean structure makes later work cheaper, safer and easier to debug. Run it to completion and treat it as one goal.

**Step 1 - Scope.** Offer two optional add-ons and do only what the user picks: (a) delete comments that merely narrate the code; (b) delete tests that could never catch a real defect and repair tests that fail without a real defect.

**Step 2 - Inventory first, edit nothing.** Walk the code with one question: if I change this piece, which other pieces must change too, and does the code make that obvious? Write down each place where the answer is wrong, with file:line, under four headings:
- **Invisible dependencies:** values or logic duplicated in several places; a module relying on a global or file written elsewhere; one feature scattered over several folders by technical layer; an unwritten rule about call order.
- **Unneeded coupling:** callers reaching into internals; stable code importing volatile code; a general-purpose function carrying a flag meant for a single workflow; thin modules whose interface mirrors their internals.
- **Dead weight:** wrappers that only forward; hooks and settings for variations that never happen; unused code.
- **Special cases:** a branch for one value, a parameter for one caller, a swallowed error, a retry or sleep, a skipped test. Each one marks a requirement the design failed to include, so use them to discover what the system really needs.

**Step 3 - Redesign from the requirements down.** Ask what the structure would look like if today's needs had been known on day one. Search for the single change that explains several problems; do not patch special cases one at a time. Every proposed fix must satisfy three tests: things that change together sit together, things that change independently are not linked, and dependencies point toward the more stable side. Record each fix in a decision log above the list of problems it resolves.

**Step 4 - Apply every fix on the log.** Remove the special cases the new design makes pointless; keep the ones the system truly needs. Do not go bug hunting separately. For comments: remove those that restate the implementation, keep those that record facts from outside the code, and let workaround notes disappear with the workaround. For tests (do this last, they are your safety net): drop tests that mirror the implementation or cannot fail; rewrite tests tied to internals to assert behavior.

**Step 5 - Re-audit until nothing worthwhile remains.** Re-run the inventory, ideally with independent sub-reviewers. Finish when: very few special cases remain, a typical change touches one place, imports only point toward stability, no worthwhile findings are left, and behavior matches the start (confirm with tests and a build).

**Working tips:** keep the decision log current so context loss costs little; generate and re-run a dependency graph; use version history to see what changes together and how often; begin where leverage is greatest; summarize sections with helpers so you can reason over the whole.

## Output template (Map mode)
`Purpose (2 lines) | Entry points | Folder-by-folder table (path, what lives there, who depends on it) | Data flow in 5 steps | Where to change X (top 5 tasks) | Danger zones | Open questions`. One page; paths must be real.

## Example
"Where is checkout handled?" -> `Checkout: app/checkout/page.tsx (UI) -> lib/cart.ts (totals) -> api/payments/route.ts (provider call). Tests: tests/checkout.spec.ts. Danger: lib/cart.ts is imported by 9 files.`

## Edge cases
- Very large repo: map the top two levels first, then drill into the area the user cares about; say what was not read.
- Generated or vendored folders: list them once as "ignore" instead of describing them.
- If you are unsure what a file does, write "unclear" rather than guessing.
