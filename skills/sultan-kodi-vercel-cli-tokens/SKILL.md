---
name: sultan-kodi-vercel-cli-tokens
description: Use the Vercel CLI non-interactively with an access token for CI or scripts, safely. Use when automating deploys.
---

# Vercel CLI with tokens

- Token lives in an environment variable (`VERCEL_TOKEN`) or the CI secret store, never in code, logs or chat.
- Pass it with `--token "$VERCEL_TOKEN"`; link a project with `vercel link --yes` and org and project ids from env.
- Pull settings with `vercel pull`, build with `vercel build`, deploy with `vercel deploy --prebuilt`; add `--prod` only on request.
- Scope tokens to the minimum team and rotate them if exposed.
- On failure, show the command and the error but redact the token.
