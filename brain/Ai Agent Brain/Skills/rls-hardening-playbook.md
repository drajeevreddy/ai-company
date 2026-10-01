# RLS hardening playbook

Concrete patterns for hardening a multi-tenant Supabase/Postgres schema. Companion to [[Skills/multi-tenant-rls-audit]]; principle in [[Skills/a-role-is-not-a-tenant]].

## 1. SECURITY DEFINER helpers, pinned search_path, never re-read the policed table
Resolve membership in a helper that runs as owner, with `search_path` pinned, and never SELECTs the table the policy is attached to (that is what caused 42P17 recursion).
```sql
create or replace function public.is_clinic_member(p_clinic uuid)
returns boolean language sql stable security definer
set search_path = public, pg_temp
as $$
  select exists (
    select 1 from public.clinic_members m
    where m.user_id = auth.uid() and m.clinic_id = p_clinic
  );
$$;
```
- `security definer` bypasses RLS inside the helper → no recursion.
- `set search_path = public, pg_temp` stops search_path hijacking; `pg_temp` last.

## 2. Derived-clinic predicates
One predicate per resource, derived from the row's clinic, so policies read cleanly:
```sql
create or replace function public.patient_in_my_clinic(p_patient uuid)
returns boolean language sql stable security definer set search_path = public, pg_temp as $$
  select exists (
    select 1 from public.patients p
    where p.id = p_patient and p.clinic_id is not null
      and public.is_clinic_member(p.clinic_id)
  );
$$;
-- same shape: appointment_in_my_clinic(), invoice_in_my_clinic()
```
Use them in policies:
```sql
create policy appointments_select on public.appointments
  for select to authenticated
  using ( public.appointment_in_my_clinic(id) );

create policy appointments_insert on public.appointments
  for insert to authenticated
  with check ( public.appointment_in_my_clinic(id) );
```

## 3. Tenant column NOT NULL + BEFORE INSERT trigger
A non-nullable tenant column stops orphan rows; a trigger derives it for legitimate writes.
Raising variant (default for rows that must be tenant-owned):
```sql
alter table public.appointments alter column clinic_id set not null;

create or replace function public.set_clinic_id_from_actor()
returns trigger language plpgsql security definer set search_path = public, pg_temp as $$
begin
  if new.clinic_id is null then new.clinic_id := public.current_clinic_id(); end if;
  if new.clinic_id is null then
    raise exception 'clinic_id is required' using errcode = '23502';
  end if;
  return new;
end $$;

create trigger trg_appointments_clinic_id
  before insert on public.appointments
  for each row execute function public.set_clinic_id_from_actor();
```
Non-raising variant for **system/service writes** that legitimately have no tenant (cron, webhooks): fill from the actor if possible, otherwise leave NULL instead of throwing.
```sql
create or replace function public.set_clinic_id_default_only()
returns trigger language plpgsql security definer set search_path = public, pg_temp as $$
begin
  if new.clinic_id is null then new.clinic_id := public.current_clinic_id(); end if;
  return new;  -- may remain null for actor-less system writes
end $$;
```
Choose the variant per table; never force a system write into a tenant.

## 4. Don't attribute actor-less audit rows to a tenant
When `activity_logs.actor_id`/`user_id` is null (system/cron), leave `clinic_id` null too. Don't infer a tenant from "the only clinic" — that mislabels global events as a tenant's and can leak through a tenant policy.

## 5. Patient self-access by verified email
Patients read their own records only when their verified email matches, never by a client-supplied id:
```sql
create policy patients_self_select on public.patients
  for select to authenticated
  using (
    public.patient_in_my_clinic(id)                 -- staff with membership
    or lower(email) = lower(auth.jwt() ->> 'email') -- verified-email self access
  );
```
Keep the email match tied to the JWT (verified), never to a request-body field.

## 6. Service role: authorized server handler vs client-reachable action
- **OK:** service-role client constructed inside an authorized server-only handler (a route/server action that first verifies the session and the target tenant), never exported to a module the client can import.
- **Bug:** service-role client in a `"use server"` action or shared `lib/` that a client component can reach — it bypasses RLS for whoever hits it.

Rule of thumb: the service role never appears on a path an unauthenticated client can invoke, and every use is scoped to the caller's tenant.

see: [[Skills/a-role-is-not-a-tenant]] · [[Skills/multi-tenant-rls-audit]] · [[Skills/rls-verification-harness]]
