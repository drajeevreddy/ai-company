# Supabase + Vercel CLI command map

Verified against Supabase CLI 2.117.x, Vercel CLI 58.x, on a linked Next.js project. Run from the app directory that holds `supabase/` and `.vercel/`.

## Supabase CLI

| Goal | Command | Notes |
|---|---|---|
| Is it installed / authed | `npx supabase --version`, `npx supabase projects list` | not on `PATH` in many installs; token lives in `~/.supabase/` |
| Project ref, region, DB version | `npx supabase projects list` | JSON; take the major version for the local Docker image |
| Link / relink | `npx supabase link --project-ref <ref>` | link state is also in `supabase/.temp/project-ref` |
| Local vs remote migrations | `npx supabase migration list --linked` | duplicated numeric prefixes show as duplicate/phantom rows |
| Drift check before pushing | `npx supabase db push --linked --dry-run` | `{"upToDate":true}` = in sync; otherwise prints the filtered SQL |
| Apply migrations | `npx supabase db push --linked` | add `--include-all` only when you understand why the CLI skipped one |
| Schema backup | `npx supabase db dump --linked -f schema.sql` | pulls `public.ecr.aws/supabase/postgres:<ver>` on first run |
| Data backup | `npx supabase db dump --linked --data-only -f data.sql` | do this before any NOT NULL/backfill migration |
| Edge functions | `npx supabase functions list` | slugs, versions, `verify_jwt` |
| Deploy a function | `npx supabase functions deploy <slug> --project-ref <ref>` | then re-run `functions list` and confirm the version bumped |
| Preview branch | `npx supabase branches create <name>` | paid orgs; on others validate in Docker instead |
| Auth settings | `curl {SUPABASE_URL}/auth/v1/settings` (read) | no CLI write path — dashboard / Management API only |

## Vercel CLI

| Goal | Command | Notes |
|---|---|---|
| Account + scope | `vercel whoami` | `vercel project ls` / `vercel domains ls` list what the scope owns |
| Which project is linked | `cat .vercel/project.json` | `{"projectId":...,"orgId":...,"projectName":...}`; `vercel link` if absent |
| Env var names | `vercel env ls production` | values stay encrypted; names are enough for planning |
| Read env values | `vercel env pull .env.local --environment=production --yes` | **sensitive vars come back as the literal `[SENSITIVE]`** |
| Set / remove | `vercel env add NAME production`, `vercel env rm NAME production` | add per environment (production, preview) |
| Deploy | `vercel --prod` | |
| Runtime logs | `vercel logs <deployment-url>` | recent requests + errors; good for confirming a deploy and spotting scanners |
| Recent deployments | `vercel ls <project>` | production URLs per deploy |

## Failure modes seen in practice

- **Pulled secret is `[SENSITIVE]` → your probe 401s.** Expected. Any test that needs the service-role key is unverifiable as written; use the anon/publishable key instead. Public keys start `eyJ...` (legacy JWT) or `sb_publishable_...`.
- **Legacy `SUPABASE_JWT_SECRET` cannot mint test JWTs** when the project signs with asymmetric keys: PostgREST answers `401 PGRST301 No suitable key or wrong key type`. Don't debug the token — test against a local harness instead.
- **Bot checkpoint on the deployment**: plain `curl` gets a challenge page for static assets; add a browser `User-Agent` and `Referer`, and treat a 403 as "challenged", not "missing".
- **`db dump` needs Docker** and downloads the Supabase postgres image on first use — expected on a cold machine.
- **`db push` with a stale local tree** reports odd local/remote pairings; reconcile the copies before pushing.
