# DocCare Security Remediation

Incident record for [[Projects/DocCare-EndoCare]]: every tenant-isolation finding from the audit, how it was fixed, and the one lesson that generalized to [[Skills/a-role-is-not-a-tenant]].

## Context
An end-to-end tenant-isolation review of the DocCare/EndoCare Supabase backend + Vercel deployment, driven by a live production incident (below) and an authenticated audit using a real account's JWT against PostgREST.

## The production incident (proof that a role is not a tenant)
A `clinic_admin` account with **no clinic membership at all** could read:
- every row in `activity_logs` (all tenants),
- every row in `profiles` — including another tenant's `super_admin`,
- a stored **plaintext NVIDIA API key** in config.

Cause: policies used `is_admin()` / `role IN ('clinic_admin','admin')` as a *standalone* predicate. A global role check is not a tenant check. Fix + doctrine: [[Skills/a-role-is-not-a-tenant]].

How it was caught: recovered the public anon key from the deployed client bundle / `vercel env pull`, then authenticated as the real account via the Supabase Auth password grant and queried PostgREST directly — the app UI never showed those rows. See [[Skills/rls-verification-harness]] and [[Skills/supabase-vercel-tooling-gotchas]].

## Findings → fixes
1. **Service-role client everywhere.** `createClient(url, SERVICE_ROLE_KEY)` imported across modules/actions → RLS bypassed process-wide, and reachable from client-invokable server actions. Fixed by consolidating to a single admin factory restricted to authorized server handlers; everything else uses the user-scoped client.
2. **Anonymous server-action reads.** Actions read with no session check (anon or service role). Fixed by requiring an authenticated user (`auth.uid()`), deriving the clinic from membership, and reading through the user client so RLS applies.
3. **RLS 42P17 infinite recursion.** A policy SELECTed the very table it was attached to (e.g. a `profiles` policy querying `profiles` to get the role). Fixed by moving the lookup into `SECURITY DEFINER` helpers with `SET search_path = public, pg_temp`, so membership resolves without re-entering RLS. See [[Skills/rls-hardening-playbook]].
4. **Signup metadata trusting `role`.** `user_metadata.role` came from the client and was written into the profile → self-promotion to `super_admin`. Fixed by ignoring client metadata for role; role is assigned server-side / least privilege.
5. **`appointments` `FOR ALL` with no clinic predicate.** Any authenticated user could read/write all appointments across tenants. Fixed with per-command policies gated by `appointment_in_my_clinic()`.
6. **Double booking.** No constraint prevented overlapping appointments for the same provider/slot. Fixed with a DB-level exclusion/unique guard so concurrent inserts cannot both win.
7. **Queue tokens via `max+1`.** Token allocation used `select max(token)+1` → race → duplicates/guessable tokens. Fixed with atomic allocation (sequence/`nextval` or a locked increment).
8. **Unauthenticated cron/ICS routes.** `/api/cron/*` and `/api/ics/*` were callable by anyone — the ICS feed leaked appointment data. Fixed so cron fails closed (401) unless `Authorization: Bearer $CRON_SECRET`, and ICS requires authenticated, clinic-scoped access or a signed token.
9. **Missing security headers.** Fixed by adding baseline headers via `next.config`/middleware.
10. **Edge functions using the service role.** Fixed so functions verify the caller's JWT and use least privilege, touching only the caller's clinic.

## Migrations 00016 → 00019 (grouped by area)
- **00016 — helpers + recursion:** `SECURITY DEFINER` helper functions (`is_clinic_member`, `current_clinic_id`, role helpers) with pinned `search_path`; rewrote recursive policies; made tenant columns `NOT NULL` with a `BEFORE INSERT` trigger.
- **00017 — identity-ish scope fixes:** derived-clinic predicates (`patient_in_my_clinic`, `appointment_in_my_clinic`, `invoice_in_my_clinic`), per-command `appointments` policies, double-booking guard, conflict-safe queue-token allocation.
- **00018 — audit / membership repair:** stop trusting signup role metadata, patient self-access by verified email, actor-less audit rows not attributed to a tenant, ICS/cron/edge hardening, and reverting an over-broad staff→clinic link made by 00017.
- **00019 — the last bare-role policies:** `lab_tests`, `auto_reminder_config` and `auto_reminder_logs` still gated on `is_admin()` with no tenant predicate (found by *re-running* the audit — see [[Skills/multi-tenant-rls-audit]]). All three got a `clinic_id` plus membership-gated policies.
- **00004 — clean-install fix (non-security):** it ALTERed `public.medicines` before `00007` created it, so a from-scratch migration run aborted there and never reached the security migrations. It now skips when the table is absent; the suite asserts every migration applies cleanly on a fresh database.

Repository state after the work: `tests/rls/` carries the harness in-repo (**44 assertions**, `npm run test:rls`), `DEPLOYMENT.md` / `SECURITY.md` / `docs/production-readiness.md` document the posture, and `supabase/config.toml` is deliberately untracked (see [[Skills/supabase-vercel-tooling-gotchas]] #7).

(The exact per-file split is approximate; content is grouped by concern.)

## Shared database across apps
One Supabase database served **several different applications** that all pointed at a single shared `clinics` row. Clinic-scoped RLS therefore could not isolate them: any predicate keyed on `clinic_id` treats those apps as one tenant. There was no discriminator column to separate them. Recommendation: a **separate Supabase project (or separate schema) per application**. Caveat: this cannot be retrofitted when no discriminator column exists — it has to be decided at design time. Pre-flight check in [[Skills/multi-tenant-rls-audit]].

## Verification
Isolation was proven with the Postgres harness (two-tenant fixtures + `SET ROLE authenticated` / `SET request.jwt.claims`), now also committed in the repo under `tests/rls/`. Pattern: [[Skills/rls-verification-harness]].

procedure: [[Skills/multi-tenant-rls-audit]] · lesson: [[Skills/a-role-is-not-a-tenant]] · project: [[Projects/DocCare-EndoCare]]
