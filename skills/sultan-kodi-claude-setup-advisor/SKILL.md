---
name: sultan-kodi-claude-setup-advisor
description: "Read-only analysis of a project that recommends Claude Code automations: MCP servers, skills, hooks, subagents and plugins, tailored to the detected stack. Use when the user wants to improve their Claude Code setup or asks what automations to add."
---

# Claude Code setup advisor

**Read-only.** Analyze the project and output recommendations; do not create or change files. The user implements them or asks separately.

## Output rules
- Recommend 1-2 of each type (the most valuable for this codebase); skip categories that do not apply.
- If the user asks about one type, focus on it and give 3-5 options.
- Go beyond generic lists: look up recommendations specific to the project's libraries when search is available.
- End by saying the user can ask for more in any category or for help implementing any item.

## Types and what they are for
- **Hooks:** automatic actions on tool events (format or lint after edits, block edits to protected files, run related tests).
- **Subagents:** specialist reviewers/analyzers working in parallel (code review, security, docs, tests).
- **Skills:** packaged workflows and expertise (`.claude/skills/<name>/SKILL.md`), invoked by the user or by Claude.
- **Plugins:** installable bundles of skills and tools.
- **MCP servers:** integrations to external systems (docs lookup, browser testing, database, GitHub, issue tracker, error monitoring, cloud, chat).

## Phase 1 - Analyze
Detect language and framework from manifests; read dependencies; check for existing Claude config (`CLAUDE.md`, `.claude/`); look at structure (source, tests, components, API, CI). Capture: stack, frontend or backend, database, external APIs, test tooling, CI/CD, issue tracker references, docs patterns, `.env` and lock files, auth or payment code.

## Phase 2 - Match signals to recommendations
- Popular libraries -> live documentation MCP. Frontend with UI tests -> browser automation MCP. Database -> database MCP. GitHub repo -> GitHub MCP. Issue tracker -> its MCP. Error tracking -> that MCP.
- Skills worth creating: API docs (with an OpenAPI template), migrations, test generation, new-component scaffolding, PR checks, release notes, project conventions (Claude-only), dev setup.
- Hooks: formatter configured -> auto-format on edit; linter -> auto-lint; TypeScript -> type-check; tests folder -> run related tests; `.env` or lock files -> block edits; security-sensitive code -> require confirmation.
- Subagents: large codebase -> code reviewer; auth/payments -> security reviewer; API project -> API documenter; performance critical -> performance analyzer; frontend heavy -> UI/accessibility reviewer; thin tests -> test writer.
- Plugins: only when a real need matches (documents, frontend design, building MCP tools).

## Phase 3 - Report
Codebase profile (type, framework, key libraries), then per category: name, why (tied to evidence in this repo), where it goes (`.claude/settings.json`, `.claude/agents/`, `.claude/skills/`), how to install. Prefer fewer, higher-value items. Be honest when nothing fits.

## Decision guide
Recommend an item only when there is concrete evidence in the repo, it saves repeated work, and it is low-risk. Prefer project-level over global changes, and flag anything that runs code automatically so the user chooses consciously.

## Example
Project: Next.js + Postgres monorepo with a flaky deploy script. Output: three recommendations, each as `what to add | why (the signal found) | effort (minutes) | where it goes`, e.g. "A pre-push hook running typecheck | repeated type errors in recent commits | 5 min | settings hooks". End with the one item to do first.

## Edge cases
- Empty or brand-new project: recommend only the basics (a short project instructions file, one verification command); do not pad the list.
- Existing setup already covers a signal: say so and skip it instead of proposing a duplicate.
- Never add anything that runs commands or reads secrets without showing the user the exact text first.
