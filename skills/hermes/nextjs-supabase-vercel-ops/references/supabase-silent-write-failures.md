# Supabase silent-write-failure audit & fix patterns

Session source: doccare/EndoCare (Next.js app, Supabase EndoCareDB, ref `cnsuyhmtbqdxsxloyljq`).
Symptom reported by user: "appointment data doesn't get stored" + "dashboard doesn't update".

## The core defect: an error-swallowing query helper

`queries.ts` wrapped EVERY DB call in `safeQuery(async () => {...}, fallback)` which
try/caught the error, logged it, and returned the fallback. Writes therefore LOOKED
successful (UI showed the toast, returned `null` row) while the insert never happened.
The dashboard "not updating" was a downstream effect: no rows → no metrics.

Fix pattern (applies to any Supabase client layer):

```ts
// reads keep the graceful fallback (empty lists, "—" metrics)
async function safeQuery<T>(fn: () => Promise<T>, fallback: T): Promise<T> {
  try { return await fn(); } catch (e) { console.error("DB query error:", e); return fallback; }
}

// writes PROPAGATE so the UI toasts the real error
async function writeQuery<T>(fn: () => Promise<T>, _fallback?: T | null): Promise<T> {
  return await fn();
}
```

Mechanical conversion: swap only the `return safeQuery(async () => {` line inside write
functions to `return writeQuery(async () => {` — the trailing `}, fallback);` still parses
(writeQuery ignores the second arg). Verify with `grep -c` per helper and confirm reads
still use safeQuery.

## Schema/code mismatch audit checklist

For each insert/update in the code, check the column ACTUALLY exists and every value
satisfies CHECK constraints. Found mismatches (all caused insert failures):

| Code wrote | DB reality | Fix |
|---|---|---|
| appointments insert without start_time/end_time | NOT NULL, no default | include both; derive end = start + 30min |
| appointments.type = "Consultation"/"Follow-up"/"New Patient" | CHECK only allowed lowercase values | normalize helper mapping UI labels → constrained values (fallback "consultation") |
| queue.status = "checked_in" | CHECK didn't include it | migration extends CHECK |
| appointment status "rescheduled" | appointment_status enum has no such value | use "scheduled" |
| activity_logs.user_name | column doesn't exist; resource_type NOT NULL | insert user_id + resource_type |
| prescriptions.status | column doesn't exist (uses is_active) | write is_active; render status from is_active |
| getDashboardMetrics selects invoices.amount | column is `total` | select total; also filter date + status_text='paid' |
| medicines / scheduled_reminders / auto_reminder_config / auto_reminder_logs / patient_notification_prefs | tables never created by any migration | new migration CREATE TABLE IF NOT EXISTS |

## Migration pattern for relaxing a live DB

```sql
-- relax a CHECK without knowing its exact name (auto-named <table>_<col>_check)
ALTER TABLE public.appointments DROP CONSTRAINT IF EXISTS appointments_type_check;
ALTER TABLE public.queue DROP CONSTRAINT IF EXISTS queue_status_check;
ALTER TABLE public.queue ADD CONSTRAINT queue_status_check
  CHECK (status IN ('waiting','called','in_consultation','completed','skipped','checked_in'));

-- give NOT NULL columns a default so older app versions stop failing
ALTER TABLE public.appointments ALTER COLUMN start_time SET DEFAULT '09:00';
ALTER TABLE public.appointments ALTER COLUMN end_time SET DEFAULT '09:30';
```

New tables must mirror the existing RLS pattern (SELECT for staff via profiles EXISTS check,
ALL policy gated by role) or the app gets empty results again. Note: `00004_pharmacy.sql`
only ALTERED a `medicines` table that no migration ever created — always verify the CREATE
exists, not just the ALTERs.

## Date/time bugs (IST clinic)

- `new Date().toISOString().split("T")[0]` at 00:30 IST = previous day UTC → "today" off by
  one. Use a local-date key helper (getFullYear/getMonth/getDate padded).
- Month-end computed as `new Date(y, m, 0).toISOString()` shifts the last day back one in
  IST. Build the last-day string locally instead.

## Verification loop

1. `npx tsc --noEmit` (needs node_modules; install first)
2. `npm run build` — on a machine without Supabase env vars, create a GITIGNORED `.env.local`
   with placeholder values or prerender fails on any page importing the Supabase client
3. `npm run lint` — see SKILL.md section 4 if `next lint` hangs
4. Confirm the Vercel auto-deploy check on the newest commit (not the old red one)
