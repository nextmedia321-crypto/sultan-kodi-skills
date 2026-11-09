---
name: sultan-kodi-browser-automation
description: Automate and test websites in a real browser with Playwright: click through flows, fill forms, capture screenshots, check that pages work. Use for end-to-end checks and scraping-free UI tasks.
---

# Browser automation with Playwright

- Check that Playwright and a browser are installed; install only if missing.
- Write a short script that: opens the URL, performs the steps, waits on visible conditions (not fixed sleeps), asserts on text or state, and saves screenshots on failure.
- Use stable selectors: role and label first, test ids second, CSS last.
- Never type real passwords or payment data; use test accounts on local or staging hosts only.
- Report: steps run, pass or fail per step, screenshot paths, and the exact error if anything failed. Keep scripts in a `tests/e2e` style folder and make them re-runnable.
