---
name: sultan-kodi-system-audit
description: "Audit an entire software system end to end: code, every screen and button, APIs, data, auth, config, deploy, tests and docs. Build a coverage ledger so nothing is skipped, list every defect by severity, propose improvements and missing features, then fix the defects in safe, verified steps. Use for a full system check, a deep audit, or fix everything."
---

# System audit and repair

Goal: leave no part of the system unexamined, report every defect and opportunity, then fix the defects safely. Work in five phases and never skip the ledger.

## Ground rules
- Evidence only: every finding cites a file and line, a command output, a screenshot or a request and response. Never report from memory or assumption.
- Never say something was tested unless you ran it. Mark each check as run, read-only review, or not checkable, with the reason.
- Never touch production, real customer data, payments, secrets, DNS or billing without a clear yes in chat. Use a local copy, staging or test data.
- Audit changes nothing. Only Phase 5 edits, and only after the user has seen the findings list.
- Do not expose secrets in reports: show the file and line, mask the value.
- Match the user's language in the reports.

## Phase 1 - Discover (no edits)
1. Identify the stack, entry points, how to run, build and test it, and where it deploys. Read the README, manifests and config first.
2. Run `scripts/inventory.py <project>` for a machine-made inventory of routes, API endpoints, interactive elements, env variables, data models, dependencies, tests and risk markers. Treat it as a starting list: add what it cannot see (generated code, other services, external dashboards).
3. If the system has a running UI, open it and walk every screen, menu, tab, modal and state with a real browser; list every button, link, form and shortcut you find, and compare with the code inventory. If it cannot run, say so and review statically.
4. Write the **coverage ledger** (see `references/coverage.md`): one row per surface, with status unchecked at first.

## Phase 2 - Examine every row
Work through the ledger until no row is unchecked. For each row apply the matching checklist in `references/coverage.md`. Typical groups: correctness, security, data integrity, error and empty states, performance, accessibility, responsiveness, copy, configuration, dependencies, observability, deploy and rollback, tests, documentation.
- For every button and form: does it have a handler, is the result visible, what happens on failure, double click, empty input, long input, slow network, logged-out state?
- For every API: authentication, authorization per role, input validation, error shape, rate limits, idempotency where relevant.
- For data: constraints, migrations, backups, deletion behavior, tenant isolation if any.
- Run what can be run: build, type check, lint, tests, dependency audit, a secret scan, the app itself. Record the exact commands and outcomes.
- A row may be closed as "not applicable" or "not checkable" only with a one-line reason.

## Phase 3 - Findings list
Produce one list, ordered by severity, each item with: id, severity (Critical, High, Medium, Low), area, what is wrong, evidence, impact, proposed fix, effort (minutes, hours, days), risk of the fix, and whether it is safe to auto-fix or needs a decision.
- Critical: data loss, security hole, broken core flow, outage risk.
- Merge duplicates, but never drop an item to shorten the list.
- End with the ledger summary: rows total, checked by running, checked by reading, not checkable (with reasons). A ledger with unchecked rows means the audit is not finished.

## Phase 4 - Opportunities
Separately list improvements and missing features, ranked by value over effort: missing states, flows users will expect, automation, monitoring and alerts, performance wins, security hardening, accessibility, onboarding, analytics, admin tools. Each with the reason it matters and a rough effort. These are proposals, not fixes: build them only on request.

## Phase 5 - Fix
Ask once for approval of the plan (which findings will be fixed, which need the user's decision), then proceed without further questions for routine fixes.
1. Create a safety point: confirm a clean git state or commit the current one, and work on a new branch. If there is no git, copy the project first.
2. Fix in severity order, in small groups of related changes, one commit per group with a message naming the finding ids.
3. After each group run the relevant checks (build, types, tests, and the affected screen or endpoint). If a fix breaks something, revert that group and report it instead of stacking changes.
4. Add a test for each fixed defect where the project has a test setup.
5. Items that need a decision, a secret, a paid change, a destructive action, a production change or a product choice are not auto-fixed. List them with the exact question.
6. Finish with a re-audit of every touched area, then a final report: fixed with evidence, not fixed with reason, new findings discovered during fixing, and the branch name for review.

## Final report format
`Summary (3 lines) | Ledger summary | Findings fixed (id, commit, proof) | Findings open (id, reason, needed decision) | Opportunities ranked | How to review and merge`.

## Edge cases
- Huge systems: audit by module, keep one ledger for the whole, and say which modules were reached in this pass.
- No access to a part (external service, another repo, a dashboard): record it as not checkable and list exactly what the user must provide.
- No tests and no way to run it: do static review, say the confidence is limited, and make fixes small and obviously safe.
- Findings that look like deliberate product behavior: ask before changing.
- Never loop on a failing fix: after two different attempts, stop and report.
