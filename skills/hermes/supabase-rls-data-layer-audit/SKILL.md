---
name: supabase-rls-data-layer-audit
description: Use when auditing Supabase RLS for cross-tenant data leaks.
---

# Supabase RLS / data-overlap audit

Test a Supabase + Next.js app for multi-tenant data overlap at the DATA layer — RLS policies, insert paths, uniqueness constraints — and for what an unauthenticated caller can reach on the live deployment. UI clicks prove nothing here.

## 1. Map the live surface (read-only)

- `vercel env pull /tmp/x.env --environment=production` in the project dir (needs the linked project). **Vercel marks some vars sensitive and writes the literal string `[SENSITIVE]`** — the anon/publishable key usually comes through; service-role and JWT secrets do not.
- Probe PostgREST with the anon key: `GET {SUPABASE_URL}/rest/v1/<table>?select=*&limit=1` with `apikey` + `Authorization: Bearer <anon>`, for every table. Record status per table.
  - `200` + rows = no RLS on that table (confirm locally with `pg_tables.rowsecurity`).
  - `401 PGRST301` = RLS active.
  - `500 {"code":"42P17"}` = policy recursion, see §3.
- `GET {SUPABASE_URL}/auth/v1/settings` reveals `mailer_autoconfirm`, `disable_signup`, enabled providers — tells you whether self-signup is usable for testing.
- A legacy `SUPABASE_JWT_SECRET` cannot mint test JWTs once the project uses asymmetric signing keys (`PGRST301 No suitable key or wrong key type`). Do not burn time there; use the local harness.
- The app's Supabase URL/anon key are baked into the deployed JS: `curl` the chunks with a browser `User-Agent` + `Referer`. Vercel's bot checkpoint ("Security Checkpoint", Code 11) blocks raw curl without those headers and blocks headless browsers entirely on some hosts.

## 2. Rebuild the schema locally and impersonate roles

```bash
docker run -d --name ec-pg -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=app \
  -p 55432:5432 postgres:16-alpine
bash scripts/apply_migrations.sh   # stub + app migrations in order
bash scripts/seed.sql              # two clinics, two staff, same-name patients
bash scripts/tests.sh              # role impersonation + overlap tests
```

`scripts/00_supabase_stub.sql` creates the only Supabase-specific surface most migrations touch: `auth.users`, `auth.uid()`/`auth.role()`/`auth.jwt()`, roles `anon`/`authenticated`/`service_role`, and a minimal `storage` schema with `buckets`, `objects` and `foldername()` — so migrations that insert into `storage.buckets` and write policies on `storage.objects` apply cleanly.

Impersonation (what PostgREST does per request):

```sql
GRANT USAGE ON SCHEMA public TO anon, authenticated, service_role;
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated, service_role;
SET ROLE authenticated;
SET request.jwt.claims = '{"sub":"<user-uuid>","role":"authenticated"}';
SELECT count(*) FROM public.patients;   -- only rows this user is entitled to
```

`SET ROLE` drops superuser, so RLS actually applies — never test as `postgres`. Run `SET ROLE anon` too, for the browser-side (anon key) paths.

If every role test comes back `42P17 infinite recursion detected in policy for relation "profiles"`, that IS a finding — but it hides the isolation behaviour underneath. Replace the self-referential policy with a `SECURITY DEFINER` helper and rerun the same suite, so you can report both the live-break and what the remaining policies actually allow:

```sql
DROP POLICY IF EXISTS "Admins can view all profiles" ON public.profiles;
CREATE OR REPLACE FUNCTION public.is_admin() RETURNS boolean
LANGUAGE sql SECURITY DEFINER STABLE AS $$
  SELECT EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role IN ('super_admin','clinic_admin'));
$$;
CREATE POLICY "Admins can view all profiles" ON public.profiles FOR SELECT USING (public.is_admin());
```

## 3. What to look for (the high-yield bugs)

- **RLS bypassed in the app.** `grep -rn 'createAdminClient\|SERVICE_ROLE' src/` — if a `"use server"` query module returns an admin client, RLS is decorative and isolation must come from the query layer. Then `grep -rn clinic_id src/`: only type definitions means nothing is scoped.
- **Policy recursion.** A policy that queries the table it protects (`ON public.profiles … USING (EXISTS (SELECT 1 FROM public.profiles …))`) → `42P17 infinite recursion detected in policy for relation`. Fix with a `SECURITY DEFINER` helper (`is_admin()`), never an inline self-reference.
- **Role taken from signup metadata.** `handle_new_user()` reading `raw_user_meta_data->>'role'` lets anyone self-register as `super_admin`/`clinic_admin`. Test by inserting into `auth.users` with that metadata and checking what the created profile can read.
- **`FOR ALL` policies with role-only predicates** (`role IN ('doctor','receptionist')`, no tenant match) — any staff role reaches every tenant's rows, including DELETE.
- **Unscoped writes.** Inserts that omit the tenant column land as `clinic_id NULL`: visible to nobody (lost data) or, under role-only policies, visible to everyone.
- **Overlap/duplicate acceptance.** No unique or `EXCLUDE` constraint on the booking key — insert 3 rows into one slot and count. Fix: `CREATE EXTENSION btree_gist; ALTER TABLE … ADD CONSTRAINT no_double_booking EXCLUDE USING gist (tenant WITH =, resource WITH =, day WITH =, tsrange(day + start, day + end) WITH &&) WHERE (status <> 'cancelled');`
- **Name-based foreign keys.** `patient_id` resolved by `.or(first_name.ilike.X,last_name.ilike.Y).limit(1)` links same-name people across tenants arbitrarily; the same string-built PostgREST filter is injectable through `,` `(` `.`.
- **Race-prone counters.** `max(x)+1` for tokens/queue numbers with no unique constraint.

## 4. Unauthenticated reach on the live app

- Enumerate Next.js server actions from the deployed bundles: fetch the route chunk (browser UA + Referer), then `grep -oE 'createServerReference\)\("[a-f0-9]+",[^)]*"[a-zA-Z]+"'` → `name id` pairs.
- Invoke a read-only action with no cookies:

```bash
curl -sS -X POST https://app.example.com/<public-route> \
  -H 'Next-Action: <action-id>' -H 'Content-Type: text/plain;charset=UTF-8' \
  -H 'Origin: https://app.example.com' --data-raw '[]'
```

`text/x-component` in the response is the RSC flight payload with the data. Public routes (kiosk/queue/portal/compare) are the ones to check; middleware often protects a route list but excludes `/api`, and API routes fall back to whatever the handler checks itself (`grep -rn createAdminClient src/app/api`). Action IDs are per-route: calling an ID from a route that does not register it 404s.

## 5. Hygiene

- Read-only against production: never invoke write/delete actions (`checkInPatient`, `uploadPatientDocument`, `deletePatientDocument`); demonstrate those locally instead. Probe booking races locally, not on prod.
- `shred -u` pulled env files when finished; they hold live keys.
- Redact PHI in evidence (names, DOB, phone, email, address, insurance, diagnosis) — keep the column list and record counts as proof.
- An app that "works" while its policies are broken usually means the service-role key is doing the work. That is the finding, not a contradiction.
