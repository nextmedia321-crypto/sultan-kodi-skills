---
name: sultan-kodi-ui-review
description: "Review interface code or a live page against web interface guidelines: accessibility, keyboard use, forms, focus, touch, motion, performance, responsive layout and content. Output terse file:line findings. Use when asked to review UI, check accessibility, audit design or UX."
---

# UI review

Review the given files, folder or URL. If none is given, ask which. Read the code (and render the page if a URL or dev server exists) and check every rule below. Output findings as `path:line - problem - fix`, grouped by severity, nothing else; if an area is clean say nothing about it.

## Interaction and accessibility
- Everything clickable is a real button or link (not a div); links navigate, buttons act.
- Full keyboard operation, visible focus ring (never remove outline without a replacement), logical tab order, no traps, Escape closes layers and focus returns to the opener.
- Icon-only controls have an accessible name; images have meaningful alt (empty alt if decorative); landmarks and a single h1 with ordered headings; `lang` and `dir` set.
- Color contrast at least 4.5:1 (3:1 large text, UI parts); color is never the only signal; respect reduced-motion and color-scheme preferences.
- Live regions or equivalent for async messages, toasts and form errors.

## Forms
- Every input has a visible label bound to it; correct type, autocomplete and inputmode; paste is not blocked.
- Validate on submit and on blur with the error next to the field, focus moved to the first error; submit button stays enabled until a request starts, then shows loading and prevents double submit.
- Do not hide the only way to recover (forgot password), warn before leaving with unsaved changes.

## Layout, touch and responsiveness
- Works from 320px up with no horizontal scroll; tap targets at least 44px with spacing; safe-area insets on mobile.
- Prevent layout shift: width/height on images and media, reserved space for async content.
- Text can grow to 200% without breaking; long words and user content wrap or truncate deliberately.

## Motion and feel
- Animate only transform and opacity, short durations, never `transition: all`; interrupted animations stay consistent.
- Distinct states: hover, focus, active, disabled, loading, empty, error, success.

## Performance
- Large lists virtualized; images sized, lazy-loaded below the fold, modern formats; no render-blocking third-party scripts; fonts with swap and preload for critical ones.

## Content and copy
- Specific button labels (verb + object), meaningful empty states, helpful error text that says how to fix, numbers formatted for the locale, consistent terms.
- Dark mode and RTL checked when the product supports them.

## Output template
`Issue | where | category | severity (High, Medium, Low) | fix`. Group by severity, put accessibility blockers first, and end with the three fixes that would improve the screen most.

## Example
`High | login form | labels missing on both inputs | screen readers cannot name the fields | add visible labels linked to the inputs`; `Medium | buttons 32px tall on mobile | below the comfortable touch size | raise to 44px`.

## Edge cases
- Only a screenshot available: review visuals and say interaction checks were not possible.
- Brand rules that conflict with a guideline: flag it as a trade-off instead of calling it a bug.
- Do not redesign the product; recommend focused fixes.

## Bundled script
`scripts/audit_html.py page.html` statically finds missing alt text, unnamed buttons, unlabeled fields, clickable divs, positive tabindex and heading jumps. `scripts/audit_html.py --contrast "#777777" "#ffffff"` returns the WCAG contrast ratio with pass or fail for normal text, large text and AAA. Use results as evidence, and still review the rendered screen by eye.
