---
name: sultan-kodi-system-audit
description: "Audit an entire software system end to end (code, every screen and button, APIs, data, auth, config, deploy, tests, docs), list every defect and improvement, then fix all defects in a verified loop that cannot be declared finished until a completion gate passes. Use for a full system check, a deep audit, or fix everything."
---

# System audit and repair, with a completion gate

Two goals: leave no part of the system unexamined, and never stop fixing until every defect is verified fixed or explicitly handed to the user. Most failures of automated repair are early stopping, partial fixes and unproven claims. This skill removes them with a ledger, a failing-first check for every defect, and a gate.

## Ground rules
- Evidence only: every finding cites a file and line, command output, a screenshot or a request and response.
- Say "fixed" only when `scripts/ledger.py verify` has passed. Phrases like "should work" or "I updated the code" are not proof.
- Never touch production, real customer data, payments, secrets, DNS or billing without a clear yes in chat. Use a local copy, staging or test data.
- Do not expose secrets in reports; mask values.
- Reports use the user's language.
- If `.audit/findings.json` already exists, read it first and resume from it instead of starting over.

## Phase 1 - Discover (no edits)
1. Identify the stack, entry points, how to run, build and test, and where it deploys. Read the README, manifests and config.
2. Run `scripts/inventory.py <project> --ledger .audit/ledger-seed.tsv` for the machine-made inventory of routes, endpoints, interactive elements, env variables, data models, dependencies, tests and risk markers. It is a starting list: add what it cannot see (generated code, other services, dashboards).
3. If the system can run, open it in a real browser and walk every screen, menu, tab, modal and state. List every button, link, form and shortcut and compare with the code inventory. If it cannot run, say so and review statically.
4. Build the coverage ledger from `references/coverage.md`: one row per surface, all unchecked.

## Phase 2 - Examine every row
Work through the coverage ledger until no row is unchecked, applying the matching checklist in `references/coverage.md`. Close a row only as run, read, not checkable (with reason) or not applicable (with reason). Run what can be run: build, type check, lint, tests, dependency audit, secret scan, the app itself, and record the exact commands.
- Every button and form: handler exists, result visible, behavior on failure, double click, empty and long input, slow network, logged-out state.
- Every API: authentication, authorization per role and per record, input validation, error shape, rate limits, idempotency.
- Data: constraints, migrations, backups, deletion, tenant isolation.

## Phase 3 - Record findings
Create the findings ledger with `scripts/ledger.py init` and add every defect with `ledger.py add --sev ... --area ... --title ... --evidence ... --check "<command>"`.
- The acceptance check is a command that fails now and will pass only when the defect is truly gone (a test, a curl asserting a status code, a grep that must find nothing, a Playwright script, a type check). Prefer automated checks over manual ones; if a UI defect has no test, write a small script that proves it.
- Severities: Critical (data loss, security hole, broken core flow, outage), High, Medium, Low.
- Merge duplicates, never drop items to shorten the list.
Show the user the list (`ledger.py report`) with the coverage summary: rows total, run, read, not checkable with reasons. A ledger with unchecked rows means the audit is not finished.

## Phase 4 - Opportunities
List improvements and missing features separately, ranked by value over effort: missing states and flows users expect, admin tools, automation, monitoring and alerts, performance, hardening, accessibility, onboarding, analytics. Proposals only; build them on request.

## Phase 5 - The repair loop
Ask once for approval of the plan: which findings will be fixed automatically and which need the user's decision. Then run the loop without further questions for routine fixes.

Setup: confirm a clean git state or commit the current one, and work on a new branch (copy the folder first if there is no git). Run the existing test suite once and record the baseline.

For each open finding, most severe first:
1. `ledger.py start ID` runs its check and records that it fails before the fix. If the check passes, rewrite it until it reproduces the defect.
2. Find the root cause, not the symptom. Fix the cause.
3. Sweep for siblings: search the whole project for the same pattern and add a finding for every other instance. Fix a defect class everywhere, not once.
4. `ledger.py verify ID` re-runs the check. Only a pass closes the finding. If it still fails, read the output and try again.
5. Run the full baseline suite for regressions. If something broke, fix it or revert that change; never stack new fixes on a broken state.
6. Commit with the finding id in the message.

Stuck rules: after two genuinely different approaches that fail, split the finding into smaller ones or mark it with `ledger.py block ID --reason "..."` stating exactly what is needed from the user. Never skip a finding silently and never mark one done without a passing check. Use `wontfix` only with the user's approval.

Needs-the-user items (product choices, secrets, rotation, paid changes, destructive actions, production changes, legal questions) are blocked with the exact question, not auto-fixed.

## Phase 6 - Re-audit until clean
When no finding is open, run a full new examination pass of the whole coverage ledger, not only the touched files, because fixes create new defects and the first pass always misses some. Record it with `ledger.py pass --new N` and add any new defects to the loop. Repeat until two consecutive passes find zero new defects.

## Completion gate
Before saying the work is finished, run `ledger.py gate`. It passes only when no finding is open or in progress and the last two passes were clean. If it fails, continue the loop; do not report completion, do not summarize as done. Never end a turn with open findings unless blocked on the user, in which case say precisely what you need.

## Long jobs and handoff
Update the ledger after every fix. For large systems work module by module with one ledger for the whole system and say which modules this pass reached. If context grows long, write `.audit/HANDOFF.md` from `ledger.py report` plus the next three steps, so a new session resumes exactly where this one stopped.

## Final report
`Summary (3 lines) | Coverage summary | Fixed (id, commit, proof) | Blocked (id, exact decision needed) | Opportunities ranked | Gate result | Branch name and how to review and merge`.

## Edge cases
- No tests and cannot run: static review only, small obviously safe fixes, confidence stated.
- No access to a part (external service, another repo, dashboard): record as not checkable and list exactly what the user must provide.
- Finding that may be deliberate product behavior: block with a question, do not change.
- A check that cannot be automated: write the manual steps, run them yourself with a browser or curl, and store the evidence in the finding.

## Bundled scripts
- `scripts/inventory.py`: static inventory and ledger seed.
- `scripts/ledger.py`: findings ledger with failing-first checks, verify, block, pass and the completion gate.
