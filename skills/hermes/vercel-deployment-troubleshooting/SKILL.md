---
name: vercel-deployment-troubleshooting
description: Fix failing Vercel deployments and red GitHub checks.
---

# Vercel Deployment Troubleshooting

Use when a GitHub commit shows a red check ("Deployment failed"), `vercel --prod` misbehaves, or cron/deploy config in vercel.json is rejected.

## Diagnose a red GitHub check
1. `gh api repos/OWNER/REPO/commits/SHA/status --jq '.state, (.statuses[] | {context, state, target_url})'` — the failing context is usually `Vercel` with "Deployment failed" + target URL.
2. `gh api .../commits/SHA/check-runs` for richer detail.
3. `vercel ls --limit 10` (deployments under your account scope), `vercel inspect <url>` (deployment status + projectId), `vercel logs <url>` — NOTE: logs are UNAVAILABLE for builds that never reached READY.
4. Re-check the commit status ~60-90s after pushing a fix → expect `success`.

## Root causes seen in practice

### Vercel Hobby cron limit (deploy-time rejection)
Hobby accounts reject ANY cron schedule running more than once per day. Exact error:
"Hobby accounts are limited to daily cron jobs. This cron expression (*/15 * * * *) would run more than once per day. Upgrade to the Pro plan to unlock all Cron Jobs features on Vercel."
Fix: change the schedule in vercel.json to at most daily (e.g. `0 9 * * *`). Multiple crons are fine as long as each runs ≤ 1/day. Warn the user about the frequency trade-off; Pro unlocks frequent runs.

### `vercel --prod` targeting the wrong (or a NEW) project
- `vercel.json` `name` is DEPRECATED (warning: "The `name` property in vercel.json is deprecated") but still influences project creation: `vercel --prod` may CREATE a new project from that name and CONNECT THE GITHUB REPO TO IT, hijacking the connection from the real project (auto-deploys then fail on the real one's checks, or the new one builds without env vars).
- Fix sequence:
  1. Get the real project's id: `vercel inspect <any-live-deployment-url>` → "Fetching project \"prj_...\"".
  2. Write `.vercel/project.json` (gitignored) with `{"projectId":"prj_...","orgId":"team_...","projectName":"<real>"}`.
  3. `vercel --prod --yes` — deploys to the real project with its env vars.
  4. Remove the stray project: `echo y | vercel project rm <stray-name>` (project rm does NOT accept --yes; pipe y).
  5. Re-assert repo connection: `echo y | vercel git connect https://github.com/OWNER/REPO` → "already connected" confirms.
- Verify live: `curl -s -o /dev/null -w "%{http_code}" https://<alias>` → 307 to /auth/login is normal for authenticated apps.

### `next lint` deprecated (Next 15) hangs automation
`next lint` is deprecated; with NO eslint config it prompts interactively ("How would you like to configure ESLint?") and exits 1 — that is NOT a code failure.
Fix: add `eslint.config.mjs` flat config (eslint 9 + @typescript-eslint; no new deps needed if installed) and change the lint script to `eslint .`.
- Ignore `.next/**`, node_modules, and `next-env.d.ts` (auto-generated; its triple-slash reference triggers @typescript-eslint/triple-slash-reference error).
- Pragmatic rules for legacy codebases: `no-explicit-any` off, `no-undef` off (TS handles), `no-empty` with allowEmptyCatch, unused-vars as WARNING with `caughtErrors: "none"`.
- `no-redeclare` gotcha: a lucide-react icon import (`Activity`) + local `interface Activity` in the same file → error. Rename the interface.
- eslint CLI exits 0 on warnings-only. NOTE: `next build` runs lint during build in Next 15 — keep 0 errors or builds fail.

### Build fails at prerender on a Supabase client without env vars
Next.js static generation runs page code at build time. If a page imports `@supabase/ssr` createServerClient (e.g. via `queries.ts` or a `use-auth` hook), the build throws "@supabase/ssr: Your project's URL and API key are required to create a Supabase client!", reported as `Error occurred prerendering page "/auth/forgot-password"`. Two environments produce this; find out which one you are in before fixing.

**Local / CI build:** create a gitignored `.env.local` with placeholders for the build only, then delete it:
```
NEXT_PUBLIC_SUPABASE_URL=https://placeholder.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=placeholder-anon-key
SUPABASE_SERVICE_ROLE_KEY=placeholder-service-role-key
```
This is a static-generation requirement, not a runtime env issue — the live deploy uses the project's own vars.

**Deployed Preview / branch build:** run `vercel env ls` and read the ENVIRONMENTS column. Vars scoped to Production only mean every Preview deployment (every branch push and every PR) dies at prerender while production keeps building fine, so the failure stays invisible until someone pushes a branch. Add the public values to Preview explicitly:
```
vercel env add NEXT_PUBLIC_SUPABASE_URL preview --value "https://<ref>.supabase.co" --yes
cat <file-holding-the-key> | vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY preview --yes   # pipe: the value never lands in the transcript
```
Verify with a real preview deploy (`vercel --yes`, no `--prod`) and expect READY. Non-public vars (`SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_SECRET_KEY`) left Production-only mean the preview build passes but preview runtime breaks on cron/reminder/admin paths — report that gap instead of silently copying a secret into Preview.

## Verify which deployment production actually serves
A CLI `vercel --prod` and the git integration's own build can both be in flight, and the LAST one to finish takes the alias. A background "deployment ready" notification is therefore not proof of what is live — it can describe a build that was already superseded.
```
vercel inspect https://<production-domain>   # id, url, created of what serves NOW
vercel ls <project>                          # recent deployments with target, status, age
```
If the domain resolves to an older deployment id than the one you just built, re-run `vercel --prod`.

## Pushing a long-lived branch to main
A push to main makes the git integration build its own production deployment, so it can land minutes after your CLI deploy. Never force; guard the fast-forward and let git refuse a non-fast-forward for you:
```
git fetch origin
git rev-list --count origin/main..BRANCH   # commits to add
git rev-list --count BRANCH..origin/main   # MUST be 0 — proves main has nothing the branch lacks
git push origin BRANCH:main
git branch -f main origin/main              # keep the local default branch honest
```
Stage only the files you changed. Unrelated tool-generated files (an agent tool's `.gitignore` entries, a `CLAUDE.md` guide) stay uncommitted unless the user asks for them.

## References
- references/doccare-vercel.md — worked example: cardzey/endocare project, cron history, stray-project cleanup.