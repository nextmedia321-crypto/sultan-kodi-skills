---
name: sultan-kodi-codebase-map
description: Map an unfamiliar codebase in one pass and write a compact guide that lets agents and people navigate it. Use when starting work on a large or messy repository.
---

# Codebase map

1. Read: root files, package manifests, entry points, config, tests layout, CI. Use search rather than opening every file.
2. Produce `CODEBASE_MAP.md` with: purpose in two sentences; directory tree with one line per important folder; how to run, test and build; the main data flow; key modules and their responsibilities; external services and env vars (names only, never values); known hazards (dead code, duplicated logic, hidden coupling); where to start for common tasks.
3. Keep it under about 200 lines so it is cheap to load into context in future sessions.
4. Mark anything uncertain as "unverified". Do not change code.
