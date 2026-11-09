---
name: sultan-kodi-vercel-cli-tokens
description: "Use the Vercel CLI with an access token instead of interactive login: locate the token safely, find the project and team, deploy, manage environment variables and inspect deployments without exposing the token. Use for token-based or automated Vercel work."
---

# Vercel CLI with tokens

Work with Vercel without `vercel login`, keeping the token out of shell history, process lists and chat.

## Step 1 - Locate the token (in order)
A) `VERCEL_TOKEN` already set in the environment: check it exists without printing it.
B) A `.env` file with `VERCEL_TOKEN`: load it into the environment for the command.
C) A `.env` entry under a different name: confirm with the user that it is the Vercel token, then map it.
D) Not found: ask the user to provide it through the safe route (set it in their environment); never ask them to paste it into chat if avoidable.
**Never** pass the token as `--token ...`, in `Authorization:` headers typed in commands, or inline like `VERCEL_TOKEN=... vercel ...`. Those appear in history and process listings. The CLI reads `VERCEL_TOKEN` from the environment on its own.

## Step 2 - Locate project and team
- Check env or `.env` for project and org IDs; otherwise `.vercel/` link files; otherwise derive the team slug from a dashboard URL the user gives (`vercel.com/<team>/<project>`). Pass the team scope explicitly.

## Deploying
- **Have project ID:** deploy directly with the ID and org in the environment, no linking needed.
- **No project ID:** check for a git remote and an existing `.vercel/` link; link, then deploy.
- **Code not cloned locally:** deploy from the remote repository.
- The `.vercel/` folder stores link info; do not commit it with secrets and do not delete it casually.
- Default to preview; production only when explicitly requested.

## Environment variables
Add for all environments or a specific one (production, preview, development); list; pull to `.env.local`; remove. Never echo values back into chat; when adding, read the value from a file or prompt, not a visible command argument.

## Inspecting
List recent deployments, inspect one, read build logs (needs a recent CLI). Use them to explain failures.

## Safety
Treat the token as a password. If it was exposed in chat or a log, tell the user to revoke and recreate it.
