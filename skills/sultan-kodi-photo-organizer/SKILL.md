---
name: sultan-kodi-photo-organizer
description: "Organize a photo library safely: find the photos, find duplicates and blurry shots, group by date, place and subject into folders, copy rather than move, ask before applying, and disclose what leaves the device. Use when the user wants to tidy phone or computer photos."
---

# Photo organizer

Guide a user who may not know the terminal: one step at a time, say what you are doing before you do it, run commands yourself, ask the user only for what only they can do (like exporting from a phone).

## Three iron rules
1. **Never delete or move originals.** Work by copying. Duplicates and blurry photos go into a "review before deleting" folder; if anything is deleted, the user does it by hand on their phone or computer.
2. **Start small.** First run on about 200 photos, show the result, and run on everything only after a clear "yes".
3. **Privacy transparency.** Do local analysis (dates, GPS, sizes, hashes, blur measure) on the computer. If photos would be sent to an outside model to understand their content, first tell the user exactly what is sent (downsized copies, not originals), to whom, and the provider's data policy, and get consent. Never write API keys back in chat.

## Flow
0. **Find the photos:** look for a Photos library on a Mac, a synced folder, a Google Takeout archive in downloads, or an exported folder. If none is found, ask one question: which phone and computer? Then give only that route (iPhone with Mac: Photos app export; Android: USB or cloud download; Takeout zips can be read without unzipping).
1. **Prepare the environment:** check Python 3.10+; install only needed libraries (Pillow, HEIC support) and only after telling the user.
2. **Scan a sample (200):** read dates (EXIF), GPS, dimensions; compute a hash for exact duplicates and a perceptual hash for near-duplicates; compute a sharpness measure for blur; group trips by GPS and date gaps; optionally classify content (people, food, documents, screenshots, nature, pets) if the user consented to a vision model.
3. **Show the plan, change nothing:** how many photos would go into each folder (by year/month, trips, subject, screenshots, documents, duplicates, blurry). Ask where to put the result (default: a new "Organized photos" folder in Pictures) and for explicit approval.
4. **Apply by copying** to the destination, keep a log (source -> destination) so it is fully reversible.
5. **Explain the review folder:** go through it, delete only what is truly unneeded, in the original library.

## Troubleshooting
No photos found: wrong folder or an incomplete download. Library permission errors on a Mac: export photos to a folder instead. HEIC will not open: install HEIC support. Photos only in the cloud: download originals first. Big archives need free space about the size of the zips.

## Output template
Before moving anything show a plan: `N photos | N duplicates | destination folders with counts | N skipped (unreadable)`. After approval show the same table as done, plus where the undo log is.

## Example
"Sort my trip photos by date": plan `2026/08 - 214 photos, 2026/09 - 98, duplicates 12 (kept the largest)`; moves happen only after a yes, and the log allows reversing every move.

## Edge cases
- Missing date metadata: use file date, label the folder "no-date", and say so.
- Name collisions: add a numeric suffix; never overwrite.
- Never upload, send or delete photos; duplicates go to a review folder, not the trash.
