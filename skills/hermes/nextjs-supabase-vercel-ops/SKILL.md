---
name: nextjs-supabase-vercel-ops
description: "Troubleshoot deployed Next.js + Supabase + Vercel web apps."
---

# Next.js + Supabase + Vercel app operations

Use when working on a deployed Next.js app backed by Supabase and hosted on Vercel
(e.g. the user's doccare/EndoCare project). Typical triggers: a GitHub "check failure"
(Vercel deploy), data that "appears saved but is never stored", dashboards that don't
update, or a request to test the live site end-to-end with a demo user.

## 1. Diagnosing a GitHub "check failure" (usually the Vercel deploy)

- No dashboard needed — query the commit status/checks from the CLI:
  `gh api repos/<owner>/<repo>/commits/<sha>/status --jq '.state, (.statuses[] | {context, state, target_url})'`
  `gh api repos/<owner>/<repo>/commits/<sha>/check-runs --jq '.check_runs[] | {name, status, conclusion, details_url}'`
- The Vercel CLI is often already authenticated on the user's machine (`vercel whoami`).
- Find deployments: `vercel ls` (or `vercel ls <scope>/<project>`). Inspect a failed one:
  `vercel inspect <deploy-url>`. Build logs are usually UNAVAILABLE for deployments that
  errored before READY — instead re-run the deploy from the CLI to surface the real error:
  `vercel --prod --yes` (this uses the project's configured env vars).

### Vercel Hobby cron limitation (rejects the whole deploy)
Hobby plans reject ANY cron schedule that runs more than once per day — AT DEPLOY TIME.
`*/15 * * * *` fails with: "Hobby accounts are limited to daily cron jobs. This cron
expression (*/15 * * * *) would run more than once per day." The site stays on the last
successful build until the fix is pushed. Fix: daily schedule, e.g. `0 9 * * *`.

### Project-linking pitfall (vercel.json `name` field)
- Running `vercel --prod` with NO local `.vercel/project.json` CREATES A NEW PROJECT named
  after vercel.json's `name` field and can hijack the GitHub repo connection away from the
  real project — then pushes auto-deploy to the wrong (env-less) project and fail.
- Fix: write `.vercel/project.json` manually with the real `projectId`/`orgId` (grab them from
  `vercel inspect <url-of-a-real-deploy>`), then `vercel --prod --yes`, delete the stray project
  (`echo y | vercel project rm <stray>`), and confirm the repo is connected to the real project
  (`echo y | vercel git connect https://github.com/<owner>/<repo>` — reports "already connected"
  if fine).
- `.vercel/` is gitignored — local link edits are never committed.

## 2. Supabase silent write failures (data "not stored", dashboards stale)

Classic symptom: UI shows success but rows never appear. Root causes seen in the wild:
- An error-swallowing query helper (`try/catch` returning a fallback) hides every insert
  failure. Fix: split writes into an error-PROPAGATING helper that throws, while reads keep
  the fallback helper. The UI then surfaces the real DB error instead of false success.
- Schema/code mismatches that break inserts:
  - NOT NULL columns without defaults (appointments.start_time/end_time)
  - CHECK constraints rejecting UI option values (appointments.type, queue.status)
  - Inserts into columns that don't exist (activity_logs.user_name → use user_id + resource_type;
    prescriptions.status → is_active)
  - Queries selecting columns that don't exist (invoices.amount → total)
  - Tables referenced by code but never created by any migration (medicines, scheduled_reminders,
    auto_reminder_config/logs, patient_notification_prefs)
- UTC date bugs: `new Date().toISOString().split("T")[0]` shifts "today" / month-end by one day
  in IST. Use local-date helpers.
- Dashboards "not updating" is usually the same write failure, plus no polling — add a 30s
  refresh interval.

Full audit checklist + fix patterns: references/supabase-silent-write-failures.md

## 3. Testing the live site end-to-end with Playwright

When the Hermes browser backend (Camofox) isn't running and computer_use can't see
flatpak-sandboxed browsers (`list_windows` returns `[]`), drive the real site headless:
- `mkdir /tmp/pwtest && cd /tmp/pwtest && npm init -y && npm i playwright && npx playwright install chromium`
- Launch chromium, walk the UI (signup → login → each module), assert data persists.

Supabase auth reality checks (needed to create a demo user):
- Project URL + anon key are NOT in raw HTML — extract them from the deployed JS chunks
  (grep chunks for `https://<ref>.supabase.co` and `eyJ...` JWTs).
- Probe auth config: `GET <url>/auth/v1/settings` with `apikey: <anon>` header →
  `mailer_autoconfirm` tells you if email confirmation is required.
- If `mailer_autoconfirm:false`, new email signups get `confirmation_sent_at` and NO session —
  you cannot log in without reading the email. Repeated signup probes also trip Supabase email
  rate limits (429 `over_email_send_rate_limit`).
- Fastest unblock: service-role key + admin API (`createUser` with `email_confirm:true`) — no
  emails, no rate limit. Alternative: user disables "Confirm email" in Supabase → Auth →
  Providers → Email.

Full recipe: references/live-site-playwright-testing.md

## 4. Next 15 legacy projects: make `npm run lint` work non-interactively

- `next lint` is deprecated in Next 15; with no ESLint config it opens an interactive
  "How would you like to configure ESLint?" prompt that hangs any non-interactive run.
- Fix: add `eslint.config.mjs` (eslint 9 flat config; use already-installed @typescript-eslint
  deps; ignore `.next`, `node_modules`, `next-env.d.ts`, `supabase/functions`), and switch the
  lint script to `eslint .` (exits 0 on warnings-only, unlike next lint).
- Pitfall: a lucide-react icon import + a same-named local interface (e.g. `Activity`) triggers
  `no-redeclare` — rename the interface, keep the icon import.
- Pre-existing unused-import warnings across a never-linted codebase are fine as warnings; only
  fix errors.

## Pitfalls

- Local `next build` on a machine WITHOUT Supabase env vars fails at prerender ("Your project's
  URL and API key are required"). Create a gitignored `.env.local` with placeholder values to
  build; never commit it. Vercel injects the real env at build time.
- Don't hammer GoTrue signup — email rate limits block real testing for ~an hour.
- Vercel deploy-check status is per-commit; a commit that failed stays red forever. Verify the
  NEWEST commit's status instead.
