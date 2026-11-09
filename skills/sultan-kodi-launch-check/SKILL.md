---
name: sultan-kodi-launch-check
description: "Pre-launch audit of a website or web app: security and exposed keys, accessibility (WCAG 2.1 AA / Israeli standard 5568), privacy policy versus what the code really collects, mobile, forms, speed, SEO and broken links. Reports first and fixes only after approval. Use before going live or when asked to check a site."
---

# Pre-launch check

A site can function and still leak a key, defeat keyboard users, or promise things in its privacy policy that the code does not do. The goal is to catch those before launch.

**Guiding rule: report first; change files only after the owner approves.** Some fixes alter brand colors, need a key rotated at a provider, or depend on facts only the owner knows. So the audit stage is strictly read-only.

## Language
Speak to the user in their own language from the first line (Hebrew for Hebrew speakers): updates, questions, report, summaries. Only code, paths and commands remain in English.

## Scope
If the user names one area (security, accessibility, privacy, design, quality = forms/speed/SEO/links) run just that; otherwise all.

## 1. Get oriented (no edits)
Look at the dependency manifest, folder layout and routes. Work out: static, SPA or server-backed; which framework; whether there is login, uploads, payments or AI calls; every form and its destination; whether a live URL exists (browser checks need one). Summarize in two or three lines and mark what does not apply.

## 2. Quick automated sweep (read-only)
- Hunt for secrets: API keys, tokens, private keys, passwords in source, git-tracked `.env` files, real values inside example env files, keys baked into built client bundles. **Mask every secret in anything you show or save.**
- Static scans: images lacking alt text, inputs lacking labels, missing `lang`/`dir`, missing viewport tag, missing title or description, `target=_blank` without `rel`, mixed content.
- Contrast: calculate WCAG ratios for each text/background pair in the styles (4.5:1 body, 3:1 large text and controls). If the brand color is the background of a button, tune the background's lightness and keep its hue.
- Tool output only gives leads. Open the code and confirm each lead before reporting it; discard false alarms without mentioning them.
- **Anything that downloads code or sends data out requires consent** (Lighthouse, axe, a dependency audit that uploads your package list). Ask once for all of them. If refused, rely on code reading and mark browser-only checks "needs manual test".

## 3. Area checks
Report only what you verified. A vague "might be vulnerable" belongs under "to check manually".
- **Security:** HTTPS and redirects; security headers; authorization enforced on the server for every sensitive action (a hidden button is not protection); input validation and injection; upload type and size limits; CORS scope; throttling on login, forms and AI endpoints; exposed admin routes; verbose error pages; vulnerable dependencies; leaked keys.
- **Accessibility:** keyboard access with visible focus and no traps, skip link, heading order, landmarks, labels, alt text, contrast, announced form errors, reduced-motion support, 200% zoom, and an accessibility statement with a contact person (unknown facts become `[placeholder]`).
- **Privacy:** compare policy text with reality: which trackers, pixels, fonts, embeds and forms collect data; consent before non-essential cookies, with refusing as easy as accepting; marketing consent separate and unticked; retention, processors and contact details stated.
- **Design and mobile:** usable at 375px without sideways scroll, touch targets of about 44px, readable text, consistent spacing and type, all interaction states present.
- **Quality:** each form submits, validates, confirms and fails visibly, never swallowing leads; page weight and image sizes; lazy loading; blocking scripts; title, description, canonical, share image, sitemap, robots, a single h1; internal link crawl for 404s and redirect chains.

## 4. The report
Write it in the user's language into `launch-report.md` at the project root; show the summary table and the critical and high items in chat. Severity scale:
- **Critical:** exploitable today or creating legal exposure today (a live key in the repo, an admin password in a public repository, a policy that contradicts the site).
- **High:** blocks launch (missing server-side authorization, a form that drops leads, pre-ticked consent).
- **Medium:** address around launch. **Low:** polish.
Critical and high items get what, where (file:line), why it matters in a sentence, and the proposed fix. Medium and low get a single line. Merge findings that share a root cause. Add the quick manual tests only a person can run and list what was not checked. Advise keeping the report out of public repositories (offer to add it to `.gitignore`). Finish by asking which findings to fix ("everything", "critical and high", or numbers) and wait.

## 5. Fixing, once approved
- Work from most to least severe; one sentence per fix; touch nothing the finding does not require.
- **Leaked keys:** removing the line is not enough. Move the secret to server-side configuration and ask the user to rotate it with the provider, since the old value lives on in history and perhaps in a deployed build.
- Brand colors: pick the nearest shade that passes, never a new palette.
- Policy or statement text: facts you cannot know stay as `[placeholder]`.
- Ask before wiring in any new third-party service.
- Re-run the same checks and present before/after counts (for instance Critical 3 to 0).

## Closing note (once)
Automated and AI checks are a strong first line, not a certification. Formal accessibility compliance is for a licensed accessibility consultant; a privacy policy covering sensitive or large-scale data deserves a lawyer's review. Never state that a check passed unless it ran.

## Example
Finding format: `[High] Missing Content-Security-Policy | evidence: response headers | fix: add header X | effort: 10 min`. Group by High, Medium, Low, then a short "ready to launch?" verdict with the blockers listed.

## Edge cases
- Site behind login or staging password: check only what is reachable and list what was not checked.
- Automated tool unavailable: do that check manually and mark it as manual.
- Never change anything before the user approves the fix list.

## Bundled script
`scripts/sweep.py <url> [max_links]` runs the read-only automated sweep (HTTPS and redirect, security headers, title, description, viewport, language, headings, image alt text, robots and sitemap, broken links) and prints findings by severity. Run it in step 2, then add the manual area checks. Needs only Python 3 and network access to the site.
