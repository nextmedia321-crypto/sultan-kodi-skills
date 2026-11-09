# sultan-kodi-skills

Original Claude Code skills by Kobi Sultan, MIT licensed. Each folder in `skills/` is a self-contained skill (`SKILL.md`).

## Install

All skills:

```
npx skills add nextmedia321-crypto/sultan-kodi-skills
```

A single skill:

```
npx skills add nextmedia321-crypto/sultan-kodi-skills --skill sultan-kodi-launch-check
```

Or copy a folder from `skills/` to `~/.claude/skills/` by hand.

`sultan-kodi-system-audit` audits a whole system and then fixes the defects on a separate branch; it asks for approval before fixing and never touches production without a clear yes.

The trading skill (`sultan-kodi-trading-desk`) is decision-support only, never places orders, and is not financial advice.
