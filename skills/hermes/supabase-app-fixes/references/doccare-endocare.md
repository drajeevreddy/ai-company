# Worked example: EndoCare (doccare) — Next.js 15 + Supabase

Session date: Aug 2026. Repo: https://github.com/drajeevreddy/doccare (branch main).
Stack: Next.js 15.2, @supabase/ssr 0.6, React 19, Vercel project "endocare-gold", hosted Supabase
project "EndoCareDB" (ref `cnsuyhmtbqdxsxloyljq`). Data layer: `src/lib/queries.ts` ("use server"
server actions) using `createAdminClient()` (service role, bypasses RLS). No env files in repo —
keys live in Vercel.

User report: "appointment data doesn't get stored and the dashboard doesn't update, there are many
issues."

## Root causes found (all were silent)

1. **`appointments` INSERT always failed** — schema has `start_time TIME NOT NULL` and
   `end_time TIME NOT NULL` with no defaults; code never supplied them. Also `type` had a CHECK
   constraint `IN ('consultation','follow_up','emergency','review','procedure')` while the UI sends
   "Consultation", "Follow-up", "Review", "New Patient". Every insert threw; `safeQuery` swallowed
   it → "Appointment scheduled!" toast with zero rows. Same bug in portal booking.
2. **Error-swallowing `safeQuery`** — single wrapper for ALL queries returned the fallback on any
   error, so writes looked successful. Reads kept it; writes switched to a `writeQuery` helper that
   propagates.
3. **`getDashboardMetrics`** selected `invoices.amount` — column is `total`. No date/status filter
   either → revenue always ₹0.
4. **`logActivity`** inserted `user_name` (column doesn't exist) and omitted required
   `resource_type` → every activity-log insert failed → "Recent Activity" always empty. Same bug in
   `api/send-reminder` and `processScheduledReminders`.
5. **`createPrescription`** inserted `status: "active"` — column doesn't exist (use `is_active`).
6. **`checkInPatient`** inserted queue `status: "checked_in"` — not in queue status CHECK
   (`waiting,called,in_consultation,completed,skipped`). Token was `count(*) + 1` (inflated by
   completed rows). Appointment status never synced to checked_in.
7. **`rescheduleAppointment`** set `status: "rescheduled"` — not in `appointment_status` enum.
8. **Tables referenced by code but never created by any migration**: `medicines` (migration 00004
   only ALTERs it), `patient_notification_prefs`, `scheduled_reminders`, `auto_reminder_config`,
   `auto_reminder_logs` → pharmacy module and the reminder cron were silently dead.
9. **UTC date keys** — `toISOString().split("T")[0]` everywhere → in IST "today" off by one after
   ~00:00 local; month-end `new Date(y,m,0).toISOString()` shifted the last day back one.
10. **FK joins on denormalized data** — rows stored with `patient_name` (no patient_id), but
    dashboard/queue/billing/prescriptions rendered `patients.first_name` from the join → "Unknown" /
    "undefined undefined".

## Fixes applied

- `queries.ts`: added `writeQuery` (propagates), `localDateKey()`, `normalizeAppointmentType()`
  (maps "Consultation"/"Follow-up"/"New Patient" → consultation/follow_up/consultation),
  `deriveEndTime()` (start+30min). `createAppointment` / portal booking now supply
  `start_time`/`end_time` and normalized `type`. 25 write functions converted from `safeQuery` to
  `writeQuery` via a Python line-walk script (reads untouched).
- `checkInPatient`: token = `max(token_number)+1` (ordered desc, limit 1), status "checked_in"
  kept (enum extended in migration), plus a best-effort update of the matching appointment
  (`patient_name`, `doctor_name`, today, status scheduled) → checked_in.
- `rescheduleAppointment`: keeps `status: "scheduled"` (no invalid enum value), updates
  start/end times.
- `logActivity` + both reminder routes: insert `resource_type` (+ optional user_id), never
  `user_name`.
- `createPrescription`: `is_active: true`; prescriptions page derives badge status from `is_active`.
- `createInvoice`: sets enum `status: "pending"` too; `markInvoicePaid` sets both `status` and
  `status_text`.
- `getDashboardMetrics`: `select("total, status_text, date")`, filters `date === localToday &&
  status_text === "paid"`.
- `getAppointmentsByMonth`: local-time month-end.
- Dashboard: 30s `setInterval` polling, local-time today, `patient_name` fallbacks for queue +
  appointments + activity user ("System" fallback). Same fallbacks added to billing, consultation,
  prescriptions, analytics pages.
- New migration `supabase/migrations/00007_fixes.sql` (idempotent): SET DEFAULT on
  appointments.start_time/end_time; DROP `appointments_type_check`; DROP + re-add
  `queue_status_check` including `'checked_in'`; CREATE TABLE IF NOT EXISTS for the 5 missing
  tables (with RLS + policies for medicines/prefs/reminders).

## Verification

- `npx tsc --noEmit` → exit 0.
- `npm run build` → exit 0, all 30 routes. Required a gitignored `.env.local` with placeholder
  Supabase keys (prerender needs `NEXT_PUBLIC_SUPABASE_URL`); removed after.
- `npm run lint` → `next lint` (Next 15) is deprecated; opens an interactive ESLint-setup prompt
  when no config exists and exits 1 — not a code failure.
- `package-lock.json` churn from `npm install` was reverted before commit.

## Deployment steps handed to user

1. Commit + push → Vercel auto-redeploys (real env keys already configured there).
2. Apply `supabase/migrations/00007_fixes.sql` to hosted Supabase (SQL Editor or `supabase db push`).
3. Test: schedule an appointment → should persist and appear on dashboard within 30s.
