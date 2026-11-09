---
name: sultan-kodi-ui-review
description: Review interface code or a live page for design quality, accessibility and UX problems against widely accepted guidelines (WCAG, platform conventions). Use for UI audits.
---

# UI review

Inspect the code or page and report issues in four groups.

1. **Accessibility (WCAG 2.2 AA):** contrast, text alternatives, keyboard access, focus visibility, ARIA misuse, form labels and errors, motion and zoom.
2. **Usability:** clear primary action, consistent patterns, feedback for loading and errors, empty states, destructive-action confirmation.
3. **Visual:** spacing consistency, type scale, alignment, color use.
4. **Responsive and performance:** touch targets of at least 44px, layout at 360px, image sizes, layout shift.

Format: severity, file:line or selector, problem, fix. Keep praise brief and specific. Prefer fixes the user can apply in minutes.
