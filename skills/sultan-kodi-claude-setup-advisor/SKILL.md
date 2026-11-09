---
name: sultan-kodi-claude-setup-advisor
description: Analyze a project and recommend which hooks, subagents, skills and MCP servers would improve Claude Code there. Use when setting up a repo for Claude Code or when the workflow feels repetitive.
---

# Claude Code setup advisor

1. Inspect the project: languages, frameworks, test and lint commands, CI, repeated manual steps visible in scripts and docs, existing `.claude` config.
2. Recommend, each with a one-line reason and the exact change:
   - **CLAUDE.md** lines that save re-explaining (commands, conventions, gotchas).
   - **Hooks** for checks that must always run (format, lint, block dangerous commands).
   - **Skills** for repeatable multi-step tasks.
   - **Subagents** for independent review or research tasks.
   - **MCP servers** only where a real external system is involved.
3. Rank by value over effort and suggest at most five items to start with.
4. Do not install or modify anything until the user approves.
