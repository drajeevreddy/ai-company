# A role is not a tenant

The single most reusable lesson from [[Projects/DocCare-Security-Remediation]].

**Rule:** `is_admin()` / `role IN (...)` is a *capability* check, not an *isolation* check. Used as a standalone RLS predicate it leaks across tenants. It must always be combined with clinic/tenant membership.

## The bug in one line
```sql
-- WRONG: anyone holding the role sees every tenant's rows
using ( public.is_admin() or public.current_role() in ('admin','clinic_admin') )
```
```sql
-- RIGHT: role only ever narrows within a tenant the caller already belongs to
using ( clinic_id is not null
        and public.is_clinic_member(clinic_id)
        and public.current_role() in ('admin','clinic_admin') )
```

## How it manifested in production
A `clinic_admin` with **no `clinic_members` row** could read:
- all `activity_logs` rows (every tenant),
- all `profiles` rows — including another tenant's `super_admin`,
- the plaintext NVIDIA API key stored in a config table.

The UI never displayed these (it filtered by the user's own clinic); the rows were reachable only by querying PostgREST directly with that user's JWT. "The app looks fine" hid it.

## How it was caught
- Recover the public Supabase URL + anon key from the deployed client bundle (or `vercel env pull` — real values for `NEXT_PUBLIC_*`).
- Authenticate as the real account with the Auth password grant to get an access token.
- Query PostgREST as that user and diff against the tenant the user actually belongs to.

Details: [[Skills/supabase-vercel-tooling-gotchas]] · [[Skills/rls-verification-harness]].

## How it was fixed
- Every tenant-scoped policy gated by a `SECURITY DEFINER` membership helper (`is_clinic_member(clinic_id)`), never a bare role check.
- Role checks kept only as an additional `AND`.
- Tenant columns made `NOT NULL` with a `BEFORE INSERT` trigger.

Patterns: [[Skills/rls-hardening-playbook]].

## Checklist (apply to any tenant app)
- [ ] Grep every policy for `is_admin` / `role IN` / `role =` used *without* a membership predicate.
- [ ] Grep for a policy that SELECTs its own table (42P17 recursion risk) — see [[Skills/rls-hardening-playbook]].
- [ ] Confirm `role` is never taken from client-supplied signup metadata.
- [ ] Prove it with two tenants + the harness, not by reading the UI.

doctrine: [[Skills/multi-tenant-rls-audit]] · record: [[Projects/DocCare-Security-Remediation]] · harness: [[Skills/rls-verification-harness]]
