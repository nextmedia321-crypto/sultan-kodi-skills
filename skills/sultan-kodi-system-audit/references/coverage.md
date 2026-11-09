# Coverage ledger and checklists

## The ledger
One row per surface. Columns: `id | surface | type | where (file or url) | status (unchecked, run, read, not checkable, not applicable) | evidence or reason | findings`.
Seed it from `scripts/inventory.py`, then add rows for everything the script cannot see. The audit is finished only when no row is unchecked.

## Surface types to enumerate
Screens and routes, buttons, links, forms and fields, modals and menus, keyboard shortcuts, API endpoints, background jobs and schedulers, webhooks, emails and notifications, data models and migrations, files and uploads, auth flows (sign up, log in, reset, logout, sessions, roles), payments if any, integrations, environment variables and secrets, build and deploy pipeline, infrastructure config, tests, docs, logging and monitoring, legal pages and consent.

## Checklists by area

**Correctness**: main flow works end to end; edge input (empty, very long, special characters, other languages, right-to-left); repeat actions (double click, refresh, back button); concurrency; time zones and dates; rounding and currency; pagination and sorting; search.

**Error and empty states**: every request has a loading, error and empty state; errors are readable and do not leak internals; retry paths exist; offline or slow network behavior.

**Security**: authentication on every non-public route; authorization per role and per record (no access to other users' data by changing an id); input validation and output encoding (injection, XSS); CSRF where cookies are used; secrets not in code or logs; security headers; dependency vulnerabilities; file upload limits and types; rate limiting on login and expensive calls; password reset and session expiry; admin routes protected.

**Data**: constraints and indexes; migrations are reversible or safe; backups exist and a restore was considered; deletion and retention; personal data handling; tenant isolation.

**Performance**: slow queries, N+1 patterns, missing caching, large bundles, unoptimized images, blocking calls, memory growth.

**Accessibility and UX**: keyboard use, focus order, labels and names, contrast, touch targets, reduced motion, readable copy, consistent terms, confirmation for destructive actions.

**Responsiveness**: phone, tablet, desktop; long text; zoom.

**Configuration and ops**: env variables documented and validated at start; separate dev, staging and production settings; health checks; logs with useful context; alerts; rollback plan; cost hot spots.

**Dependencies**: outdated or abandoned packages, known vulnerabilities, unused packages, license problems.

**Tests and docs**: coverage of critical flows, flaky tests, README that lets a new person run the system, API docs, runbooks.

**Legal and compliance (flag only, do not give legal advice)**: privacy policy and consent where personal data is collected, cookie handling, terms, accessibility obligations, industry rules relevant to the product.

## Opportunity prompts
Which flows would a user expect that are missing? What do admins need? What would reduce support requests? What can be automated? What should be monitored? Where would a small change give a large improvement?
