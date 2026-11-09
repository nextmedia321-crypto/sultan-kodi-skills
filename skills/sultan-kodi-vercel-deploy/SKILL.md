---
name: sultan-kodi-vercel-deploy
description: Deploy a web project to Vercel step by step with checks before and after. Use when the user wants a site or app online.
---

# Deploy to Vercel

1. Confirm the project builds locally (`build` script) and note framework and output.
2. Check env vars needed; list names only. Never print secret values.
3. Check the Vercel CLI is installed and the user is logged in; if not, tell the user the one command to run for login (do not handle their credentials).
4. Deploy a preview first, open it, and verify the key pages and forms work.
5. Only after the user approves, promote to production and verify the live URL, HTTPS and redirects.
6. Report the URLs, the build duration, and anything that needs follow-up (domains, env vars, analytics).
