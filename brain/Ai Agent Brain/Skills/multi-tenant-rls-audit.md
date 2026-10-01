# Multi-tenant RLS audit / tenant-isolation review

A step-by-step procedure for auditing tenant isolation in a Supabase (or plain Postgres) app. Re-apply it to any project before or around a security review. Distilled from [[Projects/DocCare-Security-Remediation]]; core principle in [[Skills/a-role-is-not-a-tenant]].

Trigger phrases: "audit RLS", "tenant isolation", "cross-tenant leak", "can user A see tenant B", "RLS review", "Supabase hardening".

## Procedure
1. **Map the tenant boundary.** Identify the tenant column (here `clinics.id` → `clinic_id`) and the membership table (`clinic_members`). List every tenant-scoped table. If multiple apps share one tenant row, flag it — RLS cannot separate them (step 9).
2. **Inventory policies.** Dump every policy with command + expressions:
   ```sql
   select schemaname, tablename, policyname, cmd, roles, qual, with_check
   from pg_policies where schemaname = 'public' order by tablename, cmd;
   ```
3. **Hunt predicate bugs.**
   - `is_admin()` / `role IN (...)` used *without* membership → cross-tenant leak ([[Skills/a-role-is-not-a-tenant]]).
   - A policy that SELECTs the table it is attached to → **42P17** recursion.
   - `FOR ALL` policies with no clinic predicate.
   - `USING` present but `WITH CHECK` missing on writes (or vice versa).
4. **Hunt client paths.** Find every `createClient(..., SERVICE_ROLE_KEY)` and classify each as *authorized server handler* (ok) vs *client-reachable action* (bug). Find server actions/routes with no session check.
5. **Hunt identity bugs.** Is `role` ever read from client-supplied signup metadata? Are actor-less audit writes being attributed to a tenant? Is there a patient self-access path, and is it bound to a verified email?
6. **Hunt integrity bugs.** Double booking (concurrent overlapping inserts); `max+1` / read-modify-write token or sequence allocation.
7. **Hunt edge/route bugs.** Unauthenticated cron routes (must fail closed when `CRON_SECRET` is unset); ICS/feed routes leaking data; edge functions running as service role.
8. **Headers & config.** Security headers; secrets sitting in tables the anon/authenticated role can read.
9. **Architecture.** If several apps share one DB/tenant row with no discriminator column, write the recommendation (separate project/schema per app) and the caveat that it cannot be retrofitted without a discriminator.
10. **Prove it, don't read it.** Stand up the harness with two seeded tenants and assert isolation. [[Skills/rls-verification-harness]].
11. **Fix in migrations**, dependency order: helpers → policies/predicates → integrity constraints → identity/audit → app/edge hardening. Re-run the harness after.
12. **Apply the standard fixes.** [[Skills/rls-hardening-playbook]].

## Re-run the audit after you fix it (this is not optional)
Fixing the *reported* leak is not the same as finishing the audit. After the
DocCare fixes, re-running step 3 over the migration set found three policies
that were **still** gating on a bare role check — `lab_tests`,
`auto_reminder_config`, `auto_reminder_logs` — i.e. exactly the doctrine breach
([[Skills/a-role-is-not-a-tenant]]) on lower-sensitivity tables that nobody had
complained about. They needed their own migration (`00019`). Assume the first
pass misses some; grep again after every fix.

## Do not let the test fixture pass vacuously
A regression suite is worthless if the fixture never reaches the state under
test. In DocCare the seed created staff with `role: "clinic_admin"` in signup
metadata, but the hardened signup trigger downgrades privileged roles to
`patient` — so the "admin" in the fixture was a `patient` with an admin *row* in
the membership table. The capability assertions passed without ever exercising
the capability. Fix: grant elevated roles explicitly in the seed the way an
administrator would (server-side), then re-check that the assertions still mean
what their names say. Verified by making a membership-less `clinic_admin` and
asserting it sees **zero** rows.

## Outputs to produce
- Findings table: finding · impact · fix · file/migration.
- The one-line generalized lesson.
- A re-runnable assertion suite.

## Do / Don't
- Do test with a *real* user's JWT against PostgREST — the UI hides leaks.
- Do treat role as capability and tenant membership as isolation.
- Don't attribute actor-less system audit rows to a tenant.
- Don't put the service role on anything a client can invoke.
- Don't store secrets in tables the anon/authenticated role can read.

Related: [[Skills/security|security]] · [[Skills/software-development|software-development]] · [[Skills/rls-hardening-playbook]] · [[Skills/rls-verification-harness]] · [[Skills/supabase-vercel-tooling-gotchas]]
