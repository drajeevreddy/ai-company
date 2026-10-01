---
name: supabase-project-operations
description: Use when operating a linked Supabase + Vercel project.
---

# Supabase + Vercel project operations

Schema drift checks, backups, migration and edge-function deploys, env/secret handling, and the DB invariants that keep multi-tenant data honest — for a Supabase project linked to a Next.js app on Vercel. Companion to `supabase-rls-data-layer-audit`, which proves whether isolation actually holds; this one is the deploy/fix side.

## 1. Verify tooling state before planning anything

The user expects the tooling state verified, not assumed, and recorded in the plan. Run these first and paste the results into whatever you hand back (a fix plan quoting "Vercel CLI installed" without the account/scope is useless):

```bash
npx supabase projects list            # ref, region, ACTIVE_HEALTHY, DB major version
npx supabase migration list --linked  # local vs remote migration state
npx supabase db push --linked --dry-run   # the drift check: {"upToDate":true}
npx supabase functions list           # slugs, versions, verify_jwt
vercel whoami                         # account + scope
vercel env ls production              # names only (values stay encrypted)
```

The Supabase CLI is often absent from `PATH` — use `npx supabase`. An already-authenticated session lives in `~/.supabase/`, so no env var is needed; if it is missing, `npx supabase login` or `SUPABASE_ACCESS_TOKEN`. The Vercel project link is `.vercel/project.json` in the app directory; `vercel link` when absent.

## 2. Back up before touching a production schema

```bash
npx supabase db dump --linked -f /tmp/pre-fix-schema.sql
npx supabase db dump --linked --data-only -f /tmp/pre-fix-data.sql
```

The first dump pulls the matching `public.ecr.aws/supabase/postgres:<version>` image if it is not cached locally. On a paid org prefer a preview branch (`npx supabase branches create <name>`); otherwise validate in Docker first and only then `db push --linked`.

## 3. Migrations

- One migration per concern, next sequential number; never edit an applied migration.
- `db push --linked --dry-run` is the drift check and prints the exact SQL that will run. After pushing, re-run `migration list --linked` and confirm both sides agree.
- Match the local harness image to the remote major version reported by `projects list` — a `postgres:16-alpine` harness against a Postgres 17 project can hide version-specific behaviour.
- Duplicate files sharing a numeric prefix produce phantom rows in `migration list` and can misorder a push. `diff` each duplicate against the canonical file and delete it only when byte-identical.

## 4. Invariants worth enforcing at the DB level

- **Overlap / double booking** — `btree_gist` plus an exclusion constraint, which blocks the second booking at write time independent of app logic:

```sql
CREATE EXTENSION IF NOT EXISTS btree_gist;
ALTER TABLE public.appointments ADD CONSTRAINT no_double_booking
  EXCLUDE USING gist (tenant_id WITH =, resource_id WITH =, day WITH =,
    tsrange(day + start_time, day + end_time) WITH &&)
  WHERE (status <> 'cancelled' AND resource_id IS NOT NULL);
```

Overlapping inserts then fail with SQLSTATE `23P01` (catch it and return a 409-style "slot already taken" to the UI, don't surface a raw Postgres error) while a back-to-back slot still inserts fine. Verify both directions before claiming it works.
- **Expression indexes**: `created_at::date` on a `timestamptz` column fails with `functions in index expression must be marked IMMUTABLE`. Add a real `date` column with a default, or index `(created_at AT TIME ZONE 'UTC')::date`.
- **Tenant columns**: make them `NOT NULL` and default them in a `BEFORE INSERT` trigger from the caller's membership row, raising when the caller has no tenant — a `NULL` tenant is either lost data or globally visible data. Backfill existing `NULL`s in the same migration and report the count.
- **Human-readable counters** (queue tokens, invoice numbers): never `max(x)+1` in one statement without a `UNIQUE (tenant, day, number)` guard; use a single-statement insert with retry on `23505`, or a per-tenant sequence.
- **"Only one open record" invariants** (an unsubmitted draft, one active session per user): a partial unique index makes it a guarantee the app cannot drift from. Order matters — the index cannot be created while duplicates exist, so dedupe in the same migration and keep the newest per key:

```sql
DELETE FROM public.soap_notes a USING public.soap_notes b
WHERE a.patient_id = b.patient_id AND a.status = 'draft' AND b.status = 'draft'
  AND (a.created_at < b.created_at OR (a.created_at = b.created_at AND a.id < b.id));

CREATE UNIQUE INDEX IF NOT EXISTS soap_notes_one_open_draft_per_patient
  ON public.soap_notes (patient_id) WHERE status = 'draft';
```

Scope it to the open state (`WHERE status = 'draft'`) so finished rows stay unconstrained — a later visit must still create its own row. Then handle the loser: the app's insert path catches `23505`, re-reads the open row and folds the write into it, or a second tab surfaces a raw constraint error to a clinician. Prove all three directions after pushing — duplicates gone, a second open insert refused with `23505`, a finished row still accepted.

## 5. Edge functions and secrets

- `npx supabase functions list` shows `verify_jwt`; check that **and** whether the function builds its client with the service-role key — `verify_jwt: true` with a service-role client still lets any authenticated user cross tenants. Bind the client to the caller's JWT so RLS applies. Redeploy with `npx supabase functions deploy <slug> --project-ref <ref>`.
- Vercel: `vercel env add <NAME> production`, `vercel env rm <NAME> production`, `vercel env ls [environment]`.
- **`vercel env pull` writes the literal string `[SENSITIVE]` for sensitive vars.** `NEXT_PUBLIC_*` values come through (they are public by design); service-role and JWT secrets do not. Never write a test or a plan step that needs to read one — and remember a pulled env file is live key material: `shred -u` it when done.
- Legacy `SUPABASE_JWT_SECRET` is dead weight once the project signs asymmetrically; remove it rather than leaving a second, unused trust path.

## 6. Handing back a fix plan

When the ask is "build a master prompt to fix all this", write one markdown file and give back its path plus the full text (it gets pasted into a coding agent). Keep to this shape:

- Header: repo, which local copy to work in, live target, then a **tooling table with the verified CLI state and the exact commands** from §1.
- One row per finding: ID, severity, the `file:line` it lives in, and the evidence that proves it.
- Phases in dependency order: DB migration → app authorization → domain fixes → route handlers/edge functions → headers → verification → project settings no CLI can set (auth confirmation, CAPTCHA, leaked-password protection, deployment protection).
- Copy-pasteable SQL/TS sketches, not descriptions; mark the snippets you actually executed against a scratch database and the ones you did not.
- Verification doubles as acceptance criteria: numbered assertions that fail before the change and pass after, split local-harness vs read-only live probes. Live probes use the anon key and unauthenticated requests only.
- Ground rules up front: branch name, one migration per concern, never disable RLS to fix RLS, service-role only behind a cron secret or after an authorization check, no writes against production during testing.
- State what you deliberately did not do (write-capable endpoints left unexercised, races probed locally only) — the user reads that as scope discipline, not as omission.

## 7. Pitfalls that cost time

- A deployment behind Vercel's bot checkpoint returns a challenge page to plain `curl`; static chunks need a browser `User-Agent` + `Referer`, and headless browsers may still fail verification. Don't read a 403 as a missing route.
- `vercel logs <url>` shows the recent request stream, which is useful for confirming a deploy and for spotting scanner traffic.
- Supabase auth settings (confirmation, signup policy, providers, CAPTCHA, JWT expiry) have **no CLI command** — `GET {SUPABASE_URL}/auth/v1/settings` reads them, the dashboard/Management API changes them. Do not promise a CLI step for them.
- `db push` against a project whose remote has migrations your local tree lacks will report odd pairings; reconcile before pushing, never force.

Reference: `references/cli-operations.md` for the full command map with flags, outputs and failure modes.
