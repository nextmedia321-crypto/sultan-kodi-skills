---
name: sultan-kodi-browser-automation
description: "Drive a real browser with Playwright to test and automate websites: open pages, read a page snapshot, click, fill forms, wait on conditions, capture screenshots, record network and storage state, and report per step. Use for end-to-end checks and UI tasks."
---

# Browser automation with Playwright

## Setup
- Check that Playwright and a browser are installed (import it, or run the CLI); install only what is missing. Prefer a CLI/session you can drive step by step; otherwise write a short script.

## Script gotchas
- ES-module scripts (`import ... from 'playwright'`) do not use `NODE_PATH`. If the import fails, run the script from a folder where `playwright` is installed, or link it into `node_modules`, or write the script as CommonJS (`require`) / use Python's `playwright` package. Run it once yourself to confirm it executes before reporting results; never report results you did not obtain.

## Core loop
1. Open the page and read a structured snapshot or the accessibility tree to find elements (more reliable than screenshots).
2. Act using stable targets: role + accessible name first, label/text second, test id third, CSS last. Never use brittle positional selectors.
3. After every action wait for a visible condition (element, text, URL, network idle), never a fixed sleep.
4. Assert on text, state or URL, and take a screenshot on failure (and at key steps when useful).
5. Close the browser and any sessions when done.

## Capabilities to use when relevant
- Navigation, back/forward, reload; keyboard (type, press, shortcuts); mouse (click, double click, hover, drag, wheel); form fill and select, check, upload files.
- Multiple tabs and dialogs (accept/dismiss deliberately); iframes.
- Save screenshots, PDFs, page snapshots.
- Read and set cookies, localStorage, sessionStorage; reuse a saved login state between runs.
- Emulate devices, viewport, geolocation, locale, color scheme, offline mode.
- Watch the console and network requests; mock or block requests to test error states; trace/record a session and generate script code from it.
- Run several named sessions in parallel when comparing flows.

## Safety
- Never enter real passwords, payment data or personal data. Use test accounts on local or staging hosts. Do not bypass CAPTCHAs.
- Do not scrape sites in violation of their terms; respect robots and rate limits.

## Report
Steps run, pass/fail per step, screenshot paths, console or network errors seen, and the exact error text when something failed. Keep re-runnable scripts in a tests/e2e style folder.
