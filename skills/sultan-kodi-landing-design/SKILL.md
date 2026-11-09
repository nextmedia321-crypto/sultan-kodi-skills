---
name: sultan-kodi-landing-design
description: "Design landing pages, portfolios and redesigns that do not look templated: read the brief, infer the direction, set variance/motion/density dials, follow hard layout rules, and run a pre-flight check. Use for marketing pages and redesigns, not dashboards."
---

# Distinctive landing page design

For landing pages, portfolios, editorial pages and redesigns. Not for dashboards, data tables or multi-step product UI. Every rule is contextual: read the brief first, then apply only what fits.

## 0. Read the room first
- Signals: page kind (SaaS, consumer, agency, event, portfolio, redesign, editorial); the user's vibe words; linked URLs, screenshots and named competitors; the real audience (procurement panel, design-minded consumer, recruiter scanning); existing brand assets (logo, color, type, photos - starting material in a redesign); quiet constraints (accessibility-first, public sector, regulated, trust-first, kids). Constraints override taste.
- Before any code, state one line: "Reading this as: <page kind> for <audience>, with a <vibe> language, leaning toward <system or aesthetic>."
- If the direction genuinely diverges, ask exactly one question. If you can infer, do not ask.
- Avoid the defaults: purple gradients, centered hero on dark mesh, three equal feature cards, glass effects everywhere, endless micro-animation loops, the same grey-on-white sans. Choose deliberately.

## 1. Three dials (set after the read; change conversationally)
- Variance: 1 symmetric and safe ... 10 experimental. Motion: 1 static ... 10 cinematic. Density: 1 airy gallery ... 10 packed cockpit. Baseline 8 / 6 / 4.
- Trust-first or regulated audiences lower all three; creative studios raise variance and motion; B2B tools raise density.

## 2. Design systems
- When the brief calls for a recognized system (government, enterprise, a named product style), use its official package and tokens instead of imitating it.
- When the brief is an aesthetic rather than a system, build tokens yourself: type scale, color roles, spacing scale, radii, shadows.

## 3. Conventions
- Use the project's existing stack; default to semantic HTML + CSS or the stack's utilities. Keep state local and minimal. One icon set, no emoji as icons or decoration unless the brand does.
- Responsive by construction (fluid type, grid, container constraints). Verify every dependency exists in the manifest before importing it.

## 4. Craft rules
- **Type:** a deliberate pair (display + text), a clear scale, comfortable line length (45-75 characters), tight tracking only on big headings.
- **Color:** one accent, neutrals with a slight tint, check contrast; avoid pure black on pure white and neon-on-dark by reflex.
- **Layout variety:** do not stack identical sections; vary rhythm (full-bleed, split, offset grid, asymmetry) while keeping alignment logic.
- **Materials:** shadows, borders and cards only when they communicate hierarchy; no nested boxes inside boxes.
- **States:** hover, focus, active, disabled, loading, empty, error for every interactive element.
- **Images:** purposeful assets over stock filler; consistent treatment; set dimensions to avoid layout shift.
- **Density:** every section earns its place; cut copy before shrinking type.

## 5. Hard layout rules (failing one means broken work)
- The hero fits the first viewport: headline at most 2 lines on desktop, subtext at most 20 words, CTAs visible without scrolling. If the value proposition cannot be said in 20 words, it is unclear.
- Hero top padding is capped (about 6rem on desktop); size type and hero asset together; sensible headline sizes (roughly 36-60px, bigger only for very short headlines).
- Hero stack is at most 4 text elements: optional eyebrow, headline, subtext, CTAs (one primary, at most one secondary). Trust logos, pricing teasers, feature bullets and avatar rows go in their own sections below.
- Navigation fits on one line at desktop and stays under about 80px tall.
- No horizontal scroll at any width; check 375, 768, 1280.

## 6. Redesigns
Audit first: list what works and must be preserved (brand, content, URLs, SEO), then what to change. Do not discard assets the client already owns.

## 7. Pre-flight before delivering
Render it and look at it at mobile and desktop widths. Confirm: design read stated, hero rules met, contrast passes, no console errors, no placeholder text, keyboard focus visible, reduced motion respected.

## Output template
Before building, state in 5 lines: audience, one promise, tone, the three dial settings, and the signature visual idea. After building: the page, a pre-flight checklist with pass or fail per item, and what to tweak next.

## Example
Brief: "boutique law firm, serious but modern". Direction: calm, high contrast, editorial serif headings, one restrained accent, a strong photo or typographic hero, one clear call to action. Reject: gradient blobs, three identical icon cards, generic stock imagery.

## Edge cases
- No brand assets: ask for logo and colors once; otherwise propose a small palette and say it is a proposal.
- User asks for a known site's look: take principles (spacing, hierarchy), never copy its layout, text or assets.
- Right-to-left languages: test the layout mirrored before delivering.
