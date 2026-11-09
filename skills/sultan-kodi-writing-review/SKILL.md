---
name: sultan-kodi-writing-review
description: "Review and fix prose against clear writing rules: plain words, short sentences, active voice, one idea per paragraph, consistent terms, honest claims, and the right tone for the reader. Use when the user asks to review, tighten or audit text, docs, copy or a page."
---

# Writing review

Review the text the user gives (a file, a pattern of files, or pasted text). If no target is given, ask which text to review.

## Method
1. Identify the reader and the goal of the text (who reads it, what should they do or understand after). If unclear, ask one question.
2. Check the text against the rules below. Report findings as `location: problem -> suggested rewrite`, terse, one per line, grouped by severity (clarity blockers first, polish last).
3. If the user asks for fixes, apply them with the smallest change that solves each problem and keep the author's voice.

## Rules
- **Lead with the point.** The first sentence of a section says what matters; background comes after.
- **Plain words.** Prefer the short common word; cut filler (very, really, basically, in order to); no jargon without a definition at first use.
- **Short sentences, active voice.** Name who does what. One idea per sentence, one topic per paragraph.
- **Concrete over vague.** Replace "improves performance" with the measured claim or example; every number has a unit and a source or context.
- **Honest claims.** Remove unproven superlatives, fake urgency and promises the product cannot keep.
- **Consistent terms.** One name per concept across the whole text; consistent capitalization, punctuation and formatting of lists, headings and buttons.
- **Structure for scanning.** Descriptive headings, lists for parallel items, steps numbered in order, no walls of text.
- **Right tone.** Match the audience; do not be cute in error messages; address the reader directly.
- **Inclusive and accessible.** No idioms that do not translate, link text that says where it goes (not "click here"), no meaning carried by color alone.
- **Language fit.** Write in the language of the text; for Hebrew keep punctuation and direction correct and avoid literal translations from English.
End with the three edits that would improve the text most.
