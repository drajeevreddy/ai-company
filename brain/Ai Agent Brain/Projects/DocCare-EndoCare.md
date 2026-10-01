# DocCare / EndoCare

Multi-tenant EMR (electronic medical records) product. Next.js 15 App Router + Supabase (Postgres) + Tailwind v4, deployed on Vercel. Also referred to as EndoCare.

| | |
|---|---|
| Repo | `/home/painarise/.superset/projects/doccare` |
| Vercel project | `cardzey/endocare` |
| Live domain | https://endocare-gold.vercel.app |
| Supabase project ref | `cnsuyhmtbqdxsxloyljq` |

Security history: [[Projects/DocCare-Security-Remediation]]. Reinforced by [[Skills/a-role-is-not-a-tenant]], [[Skills/multi-tenant-rls-audit]], [[Skills/rls-hardening-playbook]], [[Skills/rls-verification-harness]], [[Skills/supabase-vercel-tooling-gotchas]].

**Android client:** the build brief lives in the repo at `ANDROID-MASTER-PROMPT.md` (690 lines) — backend facts, security invariants, P0–P2 screen inventory, the design system ported from `globals.css`, explicit anti-AI-slop design rules, seven delivery phases, and the open decisions. Load it before starting any native client work.

## Stack
- Next.js 15, App Router (`app/`), React Server Components, Server Actions.
- Supabase: Postgres, Auth, RLS, Storage, Edge Functions, Realtime.
- Tailwind v4.
- Deployed on Vercel; scheduled jobs via Vercel Cron; external calendar feed via an ICS route.

## Structure (high level)
- `app/` — App Router routes: `(auth)` (sign-in / sign-up), `(dashboard)` (clinical UI), `/api/cron/*`, `/api/ics/*`.
- `lib/supabase/` — client factories (browser / server / admin). After the remediation the admin (service-role) client is used only inside authorized server handlers, never in a client-reachable action.
- `supabase/migrations/` — schema + RLS; `00016`–`00018` are the security-hardening migrations.
- `supabase/functions/` — Edge Functions.
- `tests/rls/` — Postgres-based RLS verification harness (see [[Skills/rls-verification-harness]]).

## Features
- Multi-tenant clinic management — clinics are the tenant boundary.
- Roles incl. `super_admin`, `clinic_admin`, staff; patients.
- Appointments/scheduling, invoicing, patient records, activity audit log, walk-in queue with tokens.
- Patient self-access (read one's own records by verified email).
- External calendar subscription (ICS) and scheduled jobs (cron).

## Data model (high level)
- `clinics` — tenant root. (Was overloaded across apps — see [[Projects/DocCare-Security-Remediation]].)
- `clinic_members` — (user ↔ clinic, role) — the membership table that must back every tenant predicate.
- `profiles` — user rows extending `auth.users`; carries role.
- `patients` — belong to a clinic.
- `appointments` — belong to a clinic + patient; double-booking prevented at the DB level.
- `invoices` — belong to a clinic.
- `activity_logs` — audit trail; clinic-scoped, with actor-less system rows deliberately left without a tenant.
- queue tokens — walk-in tokens, now conflict-safe.

Derived-clinic predicates `patient_in_my_clinic()`, `appointment_in_my_clinic()`, `invoice_in_my_clinic()` provide the tenant check for every policy.

## Deployment commands
```bash
# link once
vercel link --project endocare
npx supabase link --project-ref cnsuyhmtbqdxsxloyljq

# DB migrations
npx supabase db push --linked
npx supabase migration list --linked        # confirm applied (db push hides RAISE NOTICE)

# Edge functions (Docker bundler breaks under a 0700 $HOME -> use --use-api)
npx supabase functions deploy <name> --use-api

# Env (preview requires a branch; pass --value + --yes to stay non-interactive)
vercel env add NEXT_PUBLIC_SUPABASE_URL preview --value "https://cnsuyhmtbqdxsxloyljq.supabase.co" --yes
vercel env pull .env.production.local

# deploy
vercel --prod
```
CLI traps around these commands: [[Skills/supabase-vercel-tooling-gotchas]].
