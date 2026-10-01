# RLS verification harness

How to *prove* RLS with plain Postgres 17 — no live Supabase needed. Companion to [[Skills/multi-tenant-rls-audit]]; this is what turned an invisible leak ([[Skills/a-role-is-not-a-tenant]]) into a reproducible failure. It now also lives in the repo under `tests/rls/` (exact paths are the repo's; the pattern below is what matters).

## Shape
1. **Postgres 17** (Docker or local) — plain Postgres, not the Supabase image.
2. **A minimal `auth` stub** so migrations referencing `auth.uid()` / `auth.jwt()` run:
   ```sql
   create schema if not exists auth;
   create or replace function auth.uid() returns uuid language sql stable as $$
     select nullif(current_setting('request.jwt.claims', true)::jsonb ->> 'sub','')::uuid
   $$;
   create or replace function auth.jwt() returns jsonb language sql stable as $$
     select coalesce(current_setting('request.jwt.claims', true)::jsonb, '{}'::jsonb)
   $$;
   do $$ begin
     if not exists (select 1 from pg_roles where rolname='authenticated') then create role authenticated; end if;
     if not exists (select 1 from pg_roles where rolname='anon')          then create role anon; end if;
     if not exists (select 1 from pg_roles where rolname='service_role')  then create role service_role; end if;
   end $$;
   ```
3. **Apply the real migrations** to that DB, then **seed two tenants**: clinic A and clinic B, a member of A, a member of B, an admin with **no** membership, and one row per tenant-scoped table in each clinic.
4. **Become a user** with the session GUCs Supabase's PostgREST sets per request:
   ```sql
   set role authenticated;
   set request.jwt.claims = '{"sub":"<user-uuid-in-A>","role":"authenticated"}';
   ```
   (`set local` if you want it scoped to a transaction.)
5. **Assert isolation** with assertions that fail loudly:
   ```sql
   -- a member of A must not see another clinic's rows
   do $$ begin
     if exists (
       select 1 from public.profiles p
       join public.clinic_members m on m.clinic_id = p.clinic_id
       where m.clinic_id <> '<clinic-A>'
     ) then
       raise exception 'tenant leak: saw another clinic';
     end if;
   end $$;
   ```
6. **Run the suite** as a script; exit non-zero on any failure:
   ```bash
   psql "$DATABASE_URL" -v ON_ERROR_STOP=1 \
     -f tests/rls/seed_two_tenants.sql -f tests/rls/assert_tenant_isolation.sql
   ```

## The assertion that matters
The regression that proves the doctrine: switch to the **membership-less `clinic_admin`** and assert it sees **zero** other-tenant rows — before the fix it saw all of them.

## Notes
- `SET ROLE authenticated` + `SET request.jwt.claims` is exactly what PostgREST does per request, so a passing harness predicts production.
- Seed **two** tenants minimum; one tenant cannot reveal a leak.
- The repo copy lives at `tests/rls/` — treat its exact filenames as the repo's, this note as the intended pattern.

Related: [[Skills/multi-tenant-rls-audit]] · [[Skills/rls-hardening-playbook]] · [[Projects/DocCare-Security-Remediation]]
