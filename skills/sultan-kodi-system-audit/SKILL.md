---
name: sultan-kodi-system-audit
description: "Audit an entire software system end to end (code, every screen and button, APIs, data, auth, services, config, deploy, tests, docs), list every defect and improvement, then fix all defects in a verified loop that cannot be declared finished until a completion gate and an independent verifier pass. Use for a full system check, a deep audit, or fix everything."
---

# System audit and repair, with a completion gate

Two goals: leave no part of the system unexamined, and never stop fixing until every defect is verified fixed or explicitly handed to the user. Most failures of automated repair are early stopping, partial fixes and unproven claims. A ledger, a failing-first check per defect, regression guards, a gate and an independent verifier remove them.

## Ground rules
- Evidence only: every finding cites a file and line, command output, a screenshot or a request and response.
- Say "fixed" only when `scripts/ledger.py verify` has passed. "Should work" and "I updated the code" are not proof.
- Never touch production, real customer data, payments, secrets, DNS or billing without a clear yes in chat. Use a local copy, staging or test data. Live DB and permission tests run only against those.
- Mask secrets in every report. Reports use the user's language (`report_html.py --lang he` for Hebrew, right to left).
- Never claim a tool ran when it was not installed or could not run: record the row as not checkable with the install hint.
- If `.audit/findings.json` exists, read it and resume.

## Step 0 - Choose the mode and show the cost
Run `scripts/estimate.py <project>` and show the estimate (it is only an estimate). Offer the modes and use the one the user picks; default to check and fix:
- quick: Critical and High areas only (entry points, auth, data, secrets, build), read-only.
- check only: full coverage and ledger, no code changes.
- check and fix: full coverage, repair loop, two clean passes, gate.
- full: check and fix plus browser sweep, live DB, permission matrix, gap analysis, verifier and HTML report.
The Stop hook (below) is used in check and fix and full only.

## Phase 1 - Discover (no edits)
1. Identify stack, entry points, how to run, build and test, where it deploys. Read README, manifests, config.
2. `scripts/inventory.py <project> --ledger .audit/ledger-seed.tsv` for routes, endpoints, interactive elements, env vars, models, dependencies, tests and risk markers.
3. If there are several services or repos: `scripts/map_services.py <dir>` for service boundaries, exposed routes, outbound calls, shared databases and call/route mismatches. Add a row per service and per boundary.
4. Build the coverage ledger from `references/coverage.md`; all rows unchecked.

## Phase 2 - Examine every row
Work every row until none is unchecked; close a row only as run, read, not checkable (reason) or not applicable (reason). Apply the checklists in `references/coverage.md`, and run the tools:
- Real scanners: `scripts/sec_scan.py <project>` (npm audit, pip-audit, bandit, gitleaks, semgrep, trivy, osv-scanner, govulncheck, cargo audit, bundler-audit when installed; built-in secret patterns always). Never install tools without asking.
- Running app: `node scripts/browser_sweep.mjs <url> --save .audit/baseline.json` crawls pages, clicks every non-destructive button, and reports console errors, failed requests, dead buttons, basic accessibility, axe violations (if axe-core is installed), and load, LCP and transfer numbers. Run again with `--compare` after fixes to catch performance regressions; add `--mobile` for a phone viewport. Destructive-labeled buttons are skipped unless the user allowed them.
- Roles and ownership: write `.audit/authz.json` and run `scripts/authz_matrix.py .audit/authz.json` against a local or staging instance with test accounts (tokens from env vars). Every mismatch is a finding; a 200 where another user's record should be denied is an IDOR.
- Database: `scripts/db_check.py --sqlite file.db` (read-only), or `--postgres URL --i-confirm-not-production` only after the user confirms the database is a copy or staging.
- Build, type check, lint, tests, and the app itself. Record exact commands.
- If the system cannot run, say so and review statically.

## Phase 3 - Record findings
`ledger.py init`, then `ledger.py add --sev ... --area ... --title ... --evidence ... --check "<command>"` for every defect.
- The check fails now and passes only when the defect is truly gone (test, curl asserting status, grep that must find nothing, Playwright script, authz_matrix run). Prefer automated checks; if a UI defect has no test, write a small script that proves it.
- Severities: Critical (data loss, security hole, broken core flow, outage), High, Medium, Low. Merge duplicates, never drop items to shorten the list.
Show `ledger.py report` plus the coverage summary. Unchecked rows mean the audit is not finished.

## Phase 4 - Opportunities and gaps
Rank improvements with `references/opportunities.md` (impact on revenue, retention or risk, times confidence, over effort). In full mode, run `references/gap-analysis.md` against similar systems. Proposals only.

## Phase 5 - The repair loop (check and fix, full)
Ask once for approval of the plan: what is fixed automatically and what needs the user. Ask also before installing the Stop hook (it writes `.claude/settings.json`, a persistent setting): `python3 scripts/install_hook.py <project>`. Then `ledger.py active on`, which makes the hook block finishing until the gate passes (it releases after 12 identical blocks and says why).
Setup: clean git state or commit, new branch (copy the folder if no git), run the test suite once for the baseline.
For each open finding, most severe first:
1. `ledger.py start ID` runs the check and records that it fails before the fix. If it passes, rewrite the check.
2. Find the root cause; fix the cause.
3. Sweep for siblings across the whole project and add a finding for each instance.
4. `ledger.py verify ID`. It re-runs the check and then every earlier fixed check (cross-fix guard). If it reports REGRESSION, fix that before moving on.
5. Run the full baseline suite; if something broke, fix or revert.
6. Commit with the finding id in the message.
Stuck rules: after two genuinely different failed approaches, split the finding or `ledger.py block ID --reason "..."` with exactly what is needed. Never skip silently. `wontfix` only with approval. Product choices, secrets, rotation, paid changes, destructive or production changes, legal questions are blocked with the exact question.
Keep the fixes safe from coming back: `ledger.py export-tests` writes `.audit/regression.sh` from every fixed check; commit it with the project, and add it to the project's CI or test script if the user agrees.

## Phase 6 - Re-audit until clean
When nothing is open, run a full new pass over the whole coverage ledger, including rerunning the scanners, sweep and matrix, not only touched files. `ledger.py pass --new N`; add new defects to the loop. Repeat until two consecutive passes find zero new defects.

## Completion gate and independent verifier
Run `ledger.py gate` (it re-runs all fixed checks). It must pass before any completion claim. Then, in full mode and for any High or Critical fix, run the independent verifier from `references/verifier-prompt.md` with a fresh agent that has not seen the repair work. Its WEAK CHECK and NOT FIXED results become new findings and the loop resumes. Finally `ledger.py active off`, and offer `install_hook.py --remove`.

## Reporting
`scripts/report_html.py --lang he|en` builds `.audit/report.html`, a self-contained page with severity and status bars, every finding with proof, the gate state and the sweep summary; send or publish it when the user wants to share it.
Final message: `Summary (3 lines) | Coverage | Fixed (id, commit, proof) | Blocked (id, exact decision) | Opportunities ranked | Gate and verifier result | Branch and how to review and merge`.

## Long jobs and handoff
Update the ledger after every fix. Large systems go module by module with one ledger; say which modules this pass reached. When context grows, write `.audit/HANDOFF.md` from `ledger.py report` plus the next three steps.

## Edge cases
- No tests and cannot run: static review, small safe fixes, confidence stated.
- No access to a part (external service, other repo, dashboard): not checkable, list exactly what the user must provide.
- Possibly deliberate behavior: block with a question.
- A check that cannot be automated: write the manual steps, run them with a browser or curl, store the evidence.
- Tool missing (Playwright, scanners, psql): record the gap and the install command; do not claim coverage.

## Bundled files
- `scripts/inventory.py`, `scripts/ledger.py`, `scripts/stop_gate.py`, `scripts/install_hook.py`
- `scripts/sec_scan.py`, `scripts/browser_sweep.mjs`, `scripts/db_check.py`, `scripts/authz_matrix.py`, `scripts/map_services.py`
- `scripts/report_html.py`, `scripts/estimate.py`
- `references/coverage.md`, `references/verifier-prompt.md`, `references/gap-analysis.md`, `references/opportunities.md`
