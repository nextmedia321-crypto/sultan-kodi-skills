---
name: sultan-kodi-image-to-code
description: Turn a screenshot or mockup image into clean front-end code that matches it. Use when the user shares a design image and wants it built.
---

# Image to code

1. Study the image: list sections, components, spacing rhythm, fonts (best guess), colors (sample hex values), icons and imagery.
2. State your assumptions about framework (default: semantic HTML + CSS, or the project's existing stack) and responsive behavior.
3. Extract design tokens first: colors, font sizes, spacing scale, radii, shadows, as CSS variables.
4. Build the structure with semantic elements, then style. Use real text, not images of text.
5. Render the result, screenshot it, compare side by side with the source, and fix differences larger than a few pixels. Report what you could not match.
6. Add basic accessibility: alt text, labels, focus styles, correct heading order.
