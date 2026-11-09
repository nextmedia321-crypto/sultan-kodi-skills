---
name: sultan-kodi-launch-check
description: Pre-launch audit of a website or web app: security, accessibility, privacy, mobile, SEO and broken links, with a prioritized report. Use before going live or when the user says 'check my site before launch'.
---

# Pre-launch check

Goal: find what would embarrass or endanger the owner after launch, and report it in the user's language (Hebrew if they write Hebrew).

## Steps
1. Identify the project (framework, hosting, public URL or local dev server). Ask only if nothing can be inferred.
2. Run each area below. Prefer real evidence (curl headers, a browser run, grep) over guesses.
   - **Security:** HTTPS and redirects, security headers (CSP, HSTS, X-Frame-Options), secrets committed to the repo or exposed in client bundles, open admin routes, outdated dependencies (`npm audit` or equivalent).
   - **Privacy:** cookie banner and consent before trackers, privacy policy link, forms collecting personal data without notice.
   - **Accessibility:** alt text, label for every input, color contrast, keyboard focus, heading order, `lang` and `dir` on the html tag.
   - **Mobile:** viewport meta, tap target size, no horizontal scroll at 375px width.
   - **SEO:** title, meta description, canonical, Open Graph image, sitemap.xml, robots.txt, one h1 per page.
   - **Links:** crawl internal links and report 404s and redirect chains.
3. Score each finding: Blocker (fix before launch), Should fix, Nice to have.

## Output
A report with a one-line verdict, then findings grouped by severity. Each finding: what, where (URL or file:line), why it matters, how to fix. End with the 3 fixes that give the most value for the least effort. Never claim a check passed if it was not actually run; list skipped checks explicitly.
