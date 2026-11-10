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

## Prime directive: do not stop early
When the user asks to find and fix everything, the job is the whole coverage ledger plus the repair loop, not a discovery report. The cost estimate is information for the user, never a reason to stop: if the system is large, split it into modules and keep going module after module in the same run. Stop only when the gate passes, when a budget the user set is reached (`budget.py check` exit 4), or when blocked on a decision only the user can make. Ending after Phase 1 or 2 with "the full audit is not realistic in one session" is a failure. Run `ledger.py coverage` after each module and continue with the next unchecked rows.
Speed: for systems with many modules, start one subagent per module group (Agent tool, read-only examination), each writing its findings with `ledger.py add` and closing its rows with `ledger.py cover ROWID run|read|not-checkable|n/a --reason EVIDENCE`, then merge and run the repair loop on the combined ledger. Close every row with evidence; a row is never closed by saying "looks fine".

## Go-live goal
When the user says the system must be ready to go live (production-ready, "מוכנה לאוויר", launch, ship), the job is a release-ready system after one command, and a large run is explicitly fine: do not ask about cost, do not stop at a report. Do everything below in one run: full mode, every coverage row closed, every defect fixed or blocked with the exact decision, two clean passes, verifier, then `ledger.py release-set --build "..." --test "..." --smoke "..."` with the project's real build, test and smoke commands (write a smoke script that hits the main flows if none exists) and `ledger.py release`. The answer is GO or NO-GO with the reasons. Only GO means ready. Anything that needs the user (secrets to rotate, production environment settings, paid upgrades, product decisions) is listed as a NO-GO reason with the exact action. The skill never deploys to production or changes live systems itself: deployment is a separate step that needs the user's yes.

## Step 0 - Choose the mode and show the cost
Run `scripts/estimate.py <project>` and show the estimate (it is only an estimate). Offer the modes and use the one the user picks; default to check and fix:
- quick: Critical and High areas only (entry points, auth, data, secrets, build), read-only.
- check only: full coverage and ledger, no code changes.
- check and fix: full coverage, repair loop, two clean passes, gate.
- full: check and fix plus browser sweep, live DB, permission matrix, gap analysis, verifier and HTML report.
- pr: only what a change touched, for pull requests and CI (`scripts/pr_check.py`).
- monitor: a lightweight nightly re-check that reports only what changed (`scripts/monitor.py`).
The Stop hook (below) is used in check and fix and full only. In those modes turn repair mode on right after the ledger seed is written (`ledger.py active on`), so the gate also blocks finishing while any coverage row is unchecked.
Budget: if the user gives a usage cap (for example "up to 20% of my week"), run `scripts/budget.py set ...`, log rough units after heavy steps with `budget.py log N`, and run `budget.py check` between findings: exit 3 means wrap up, exit 4 means stop, save the ledger and write `.audit/HANDOFF.md`. The numbers are self-reported estimates; say so.

## Phase 1 - Discover (no edits)
1. Identify stack, entry points, how to run, build and test, where it deploys. Read README, manifests, config.
2. `scripts/inventory.py <project> --ledger .audit/ledger-seed.tsv` for routes, endpoints, interactive elements, env vars, models, dependencies, tests and risk markers.
3. If there are several services or repos: `scripts/map_services.py <dir>` for service boundaries, exposed routes, outbound calls, shared databases and call/route mismatches. Add a row per service and per boundary.
4. Build the coverage ledger from `references/coverage.md`; all rows unchecked.

## Phase 2 - Examine every row
Work every row until none is unchecked; close a row with `ledger.py cover ROWID run|read|not-checkable|n/a --reason EVIDENCE` (`ledger.py coverage` shows what is left). The completion gate fails while any coverage row is unchecked. Apply the checklists in `references/coverage.md`, and run the tools:
- Real scanners: `scripts/sec_scan.py <project>` (npm audit, pip-audit, bandit, gitleaks, semgrep, trivy, osv-scanner, govulncheck, cargo audit, bundler-audit when installed; built-in secret patterns always). Never install tools without asking.
- Running app: `node scripts/browser_sweep.mjs <url> --save .audit/baseline.json` crawls pages, clicks every non-destructive button, and reports console errors, failed requests, dead buttons, basic accessibility, axe violations (if axe-core is installed), and load, LCP and transfer numbers. Run again with `--compare` after fixes to catch performance regressions; add `--mobile` for a phone viewport. Destructive-labeled buttons are skipped unless the user allowed them.
- Roles and ownership: write `.audit/authz.json` and run `scripts/authz_matrix.py .audit/authz.json` against a local or staging instance with test accounts (tokens from env vars). Every mismatch is a finding; a 200 where another user's record should be denied is an IDOR.
- Database: `scripts/db_check.py --sqlite file.db` (read-only), or `--postgres URL --i-confirm-not-production` only after the user confirms the database is a copy or staging.
- Static tools need no running app and run in every mode, including check only: `inventory.py`, `sec_scan.py`, `pii_map.py`, `cost_scan.py`, `git_secrets.py`, `deploy_check.py`, `content_seo.py <folder>`, `email_check.py --templates`. Live tools need a running local or staging instance and a yes from the user: `browser_sweep.mjs`, `authz_matrix.py`, `fuzz.py`, `loadtest.py`, `db_check.py` on a real database. Never say a static tool "needs a running instance"; run it, and mark only the live tools not checkable.
- Hostile input: `scripts/fuzz.py config.json` against a running local or staging instance (5xx, leaked stack traces or SQL errors, unescaped reflection). Load: `scripts/loadtest.py <url> --users 20 --seconds 10` (local or staging only; refuses others without `--force` and a user yes).
- Backups: `scripts/backup_restore.py --sqlite db` or `--archive file` proves a restore works on a temp copy; a Postgres dump is only parsed unless the user provides an EMPTY throwaway database (`--pgdump dump.sql --scratch URL --i-confirm-not-production`); without it record the restore as not checkable.
- Personal data: `scripts/pii_map.py <project>` (where personal data lives, is logged or sent out; deletion, export, consent, retention code present or not). Flags for review, not legal advice.
- Git history: `scripts/git_secrets.py <project>` finds secrets removed from the code but still in history. A hit means rotate first; rewriting history only with the user's yes.
- Cost: `scripts/cost_scan.py <project>` (paid or AI calls in loops, no cache, no output cap, polling, unbounded queries). Money figures are rough and must be checked against the provider's prices.
- Content and SEO: `scripts/content_seo.py <folder|url>` (titles, meta, h1, lang, RTL, alt, canonical, Open Graph, broken internal links, duplicates).
- Email: `scripts/email_check.py --domain d.com` (SPF, DKIM, DMARC; says NOT CHECKED when DNS is unreachable and never guesses) and `--templates folder`.
- Deployment: `scripts/deploy_check.py <project>` (env vars used vs documented, health check, CI, rollback, debug flags, container user). Staging versus production differences need access to both: ask, do not assume.
- Build, type check, lint, tests, and the app itself. Record exact commands.
- If the system cannot run, say so and review statically.

## Phase 3 - Record findings
`ledger.py init`, then `ledger.py add --sev ... --area ... --title ... --evidence ... --check "<command>"` for every defect.
- The check fails now and passes only when the defect is truly gone (test, curl asserting status, grep that must find nothing, Playwright script, authz_matrix run). Prefer automated checks; if a UI defect has no test, write a small script that proves it.
- Severities: Critical (data loss, security hole, broken core flow, outage), High, Medium, Low. Merge duplicates, never drop items to shorten the list.
Optional fields on `add`: `--impact revenue|retention|risk|none`, `--effort S|M|L`, `--plain "one plain sentence for the business owner"`.
Every finding goes into the ledger with `ledger.py add`, also in check-only mode, and a Critical stays open until a check proves otherwise (an analysis that conditions are not met is not a proof; record that reasoning in `--evidence` and write the check that would confirm it). Show `ledger.py report` plus the coverage summary. Unchecked rows mean the audit is not finished.

## Phase 4 - Opportunities and gaps
Run `ledger.py priority` to turn the open findings into Today, This week and This month by business impact and effort. Rank improvements with `references/opportunities.md` (impact on revenue, retention or risk, times confidence, over effort). In full mode, run `references/gap-analysis.md` against similar systems. Proposals only.

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
`scripts/trend.py snapshot` after each pass and `trend.py compare` to show what is new, closed or reopened since last time. `scripts/report_html.py --lang he|en [--plain]` builds `.audit/report.html`, a self-contained page with severity and status bars, every finding with proof, the gate state and the sweep summary; send or publish it when the user wants to share it.
With `--plain` each finding gets a sentence a business owner understands, and the final message explains what each result means for the business without jargon.
Final message: `Summary (3 lines) | Coverage | Fixed (id, commit, proof) | Blocked (id, exact decision) | Opportunities ranked | Gate and verifier result | Branch and how to review and merge`.

## Continuous monitoring
Only with the user's approval of a specific project, set a scheduled task that runs `python3 scripts/monitor.py <project> [--url <staging>]` nightly and sends `.audit/monitor/latest.md` only when something is new. It is read-only on the project. Never schedule against a project the user did not name.

## Long jobs and handoff
Update the ledger after every fix. Large systems go module by module with one ledger; say which modules this pass reached. When context grows, write `.audit/HANDOFF.md` from `ledger.py report` plus the next three steps.

## Edge cases
- No tests and cannot run: static review, small safe fixes, confidence stated.
- No access to a part (external service, other repo, dashboard): not checkable, list exactly what the user must provide.
- Possibly deliberate behavior: block with a question.
- A check that cannot be automated: write the manual steps, run them with a browser or curl, store the evidence.
- Tool missing (Playwright, scanners, psql): record the gap and the install command; do not claim coverage.

## Bundled files
- `scripts/inventory.py`, `scripts/ledger.py` (includes `release` GO/NO-GO), `scripts/stop_gate.py`, `scripts/install_hook.py`
- `scripts/sec_scan.py`, `scripts/browser_sweep.mjs`, `scripts/db_check.py`, `scripts/authz_matrix.py`, `scripts/map_services.py`
- `scripts/report_html.py`, `scripts/estimate.py`, `scripts/trend.py`, `scripts/budget.py`, `scripts/monitor.py`, `scripts/pr_check.py`
- `scripts/fuzz.py`, `scripts/loadtest.py`, `scripts/backup_restore.py`, `scripts/pii_map.py`, `scripts/git_secrets.py`, `scripts/cost_scan.py`, `scripts/content_seo.py`, `scripts/email_check.py`, `scripts/deploy_check.py`
- `references/coverage.md`, `references/verifier-prompt.md`, `references/gap-analysis.md`, `references/opportunities.md`
