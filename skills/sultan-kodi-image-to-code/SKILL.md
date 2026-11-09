---
name: sultan-kodi-image-to-code
description: "Turn a design image (or a reference image you generate first) into clean front-end code that matches it: deep analysis, tokens, build, then render and compare. Use when the user shares a mockup or screenshot, or asks for an image-first website design."
---

# Image to code

Workflow: image first, code second. The image is the design source of truth.

## 1. Get the reference image
- If the user supplied a design image, use it. If they want a new design and an image-generation tool is available, generate the reference design image first (one per major page or section set) and only then code. If no image tool exists, say so and write a precise written design brief instead; do not pretend an image exists.
- Generate enough images to cover the whole page (hero, each major section, key states, mobile view when relevant). Do not crop an older image to stand in for a new section, and do not reuse an image whose layout was already rejected: re-generate fresh instead.
- If a detail is too small to read, request or generate a close-up of that area rather than guessing.

## 2. Analyze deeply and cleanly
- List sections top to bottom; for each: layout structure, alignment, spacing rhythm, type scale and weights, colors (sample real values), borders, radii, shadows, icons, imagery, and interactive hints.
- Write the analysis as a clean specification, not a vague impression. Note what is ambiguous and state your assumption.

## 3. Design quality rules while interpreting
- **Hero minimalism:** one clear headline, short subtext, one primary action; no stacked badges, tiny taglines or feature lists inside the hero; first view must work on mobile.
- **No nested boxes:** avoid cards inside cards inside panels; use spacing and alignment first.
- **Reduce micro-UI clutter:** cut decorative chips, tiny labels and redundant icons that do not carry meaning.
- **Image system:** one consistent visual language (lighting, style, crop) across the page; each section image has a job.
- When designing from scratch, vary the direction on purpose (theme, background character, type character, hero architecture, section system, signature components, motion language) so the result is not the generic default.
- If the user gave a reference website, borrow its structure and quality bar, not its assets or wording.

## 4. Build
1. Extract tokens first as CSS variables: colors, type scale, spacing, radii, shadows.
2. State the stack (default: semantic HTML + CSS, or the project's own) and responsive behavior.
3. Build structure with semantic elements, then style. Real text, never images of text. Real image assets from the design where needed.
4. Add accessibility: alt text, labels, focus styles, heading order, contrast.

## 5. Verify
Render the page, screenshot it at the image's width and at mobile width, compare side by side with the source, and fix every difference larger than a few pixels (spacing, size, color, alignment). Report what you could not match and why. Never claim a match you did not check.
