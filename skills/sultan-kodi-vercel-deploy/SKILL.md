---
name: sultan-kodi-vercel-deploy
description: "Deploy a project to Vercel safely: gather state, pick the right method (git push, CLI deploy, link first, or auth first), always preview first, production only on explicit request, and always show the deployment URL. Use when the user says deploy, push live or give me a link."
---

# Deploy to Vercel

Always deploy as **preview** unless the user explicitly asks for production. Production needs a clear yes in chat. The long-term goal is a project linked to Vercel with git-push deploys, so each method should move the user toward that.

## Step 1 - Gather state (run all four checks)
1. Is there a git remote (`git remote get-url origin`)?
2. Is the folder linked (`.vercel/project.json` or `.vercel/repo.json`)?
3. Is the Vercel CLI installed and authenticated (`vercel --version`, `vercel whoami`)?
4. If authenticated, list teams. With several teams, ask which one; with one, use it.

## Step 2 - Choose the method
- **Linked + git remote:** commit and push; the push creates the preview deployment. Find the URL with `vercel ls`, or tell the user to check the dashboard or commit status.
- **Linked, no remote:** `vercel deploy` (preview), without waiting if long; check with `vercel inspect <url>`.
- **Not linked, CLI authenticated:** link first (`vercel link`, confirm team and project), then deploy.
- **Not linked, CLI not authenticated:** install the CLI if missing, authenticate (the user completes login or provides a token the safe way), link, then deploy.
- **No authentication possible (sandbox):** use the platform's no-auth fallback that returns a preview URL plus a claim URL, and tell the user to claim it to keep it.

## Safety
- Never put tokens in commands, URLs or chat; use environment variables.
- Do not commit `.env` files or secrets; check before pushing.
- Never deploy to production, change domains or delete deployments without explicit approval.
- Do not change the project's build settings unless that is the problem.

## Output (always)
Show the deployment URL, the method used and the build status. For no-auth fallback show both preview and claim URLs. If the build failed, show the key error lines and propose the fix.

## Troubleshooting
- Network blocked in a sandbox: say so and ask the user to allow the domain or deploy from their machine.
- CLI auth failure: re-authenticate; check the right team scope.
- Build fails: reproduce locally with the build command, fix, redeploy.

## Example
"Deploy this" in a linked project with a git remote: commit, push, then report `Method: git push | Status: building | Preview: <url> | Next: say "production" to promote`. Production is never started without that word.

## Edge cases
- Dirty working tree: show what would be committed and ask before committing.
- Several teams or projects match: ask which one, do not guess.
- Build fails: show the key error lines, propose the fix, and do not retry blindly.
