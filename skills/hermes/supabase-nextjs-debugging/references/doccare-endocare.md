# EndoCare / doccare worked example

Next.js 15.5 + Supabase (EndoCareDB) + Vercel. Repo: github.com/drajeevreddy/doccare (branch main). Fixes committed 2026-08-05 (930bc59, 9e9c173, 07597eb) and deployed.

## Stack facts
- Supabase project ref: cnsuyhmtbqdxsxloyljq ("EndoCareDB"). No env keys in repo — DB not directly queryable from dev box; fix code + migrations instead.
- Queries layer: src/lib/queries.ts — ALL reads AND writes went through `safeQuery(fn, fallback)` which swallowed errors. ~26 write functions converted to `writeQuery` (propagates). Reads (34) kept safeQuery for empty states.
- Activity logging: `activity_logs` has NO user_name column and REQUIRES resource_type — every logActivity insert was failing silently. Fix: insert user_id + resource_type ("activity"/"reminder"). Pages render `act.user_name || "System"`.

## Bugs fixed (in src/lib/queries.ts + pages)
1. createAppointment: inserted without start_time/end_time (NOT NULL, no default) + type "Consultation"/"New Patient" violated appointments_type_check → insert ALWAYS failed. Fixed: derive start/end times (30-min end), normalizeAppointmentType() map → constrained lowercase values.
2. rescheduleAppointment wrote status "rescheduled" — not in appointment_status enum → failed. Now 'scheduled'.
3. checkInPatient: token = count+1 (wrong), 'checked_in' not in queue CHECK, appointment status never updated. Fix: max token + 1, update appointment to checked_in, queue row.
4. getDashboardMetrics: selected invoices.amount (column is total) → revenue always 0; no date filter; paid tracked via status_text. Rewrote with total + local-date filter + status "paid".
5. getAppointmentsByMonth: toISOString month-end bug (IST) → last day of month missing from month view. Fixed with local lastDay.
6. createPrescription: inserted status:"active" — column doesn't exist → insert failed. Uses is_active; UI renders status from is_active.
7. API routes (send-reminder, process-reminders) inserted activity_logs.user_name → fixed to resource_type.
8. Medicines/reminders tables referenced but never created by migrations — migration 00007 creates them.
9. Patient-name displays (dashboard/billing/consultation/prescriptions) rendered patients FK join (always null because rows store patient_name) → "Unknown". Added patient_name fallback everywhere.

## Migration 00007_fixes.sql (must be applied to hosted DB!)
- appointments.start_time/end_time SET DEFAULT '09:00'/'09:30'
- DROP appointments_type_check; extend queue_status_check with 'checked_in'
- CREATE TABLE IF NOT EXISTS: medicines, patient_notification_prefs, scheduled_reminders, auto_reminder_config, auto_reminder_logs (+ RLS policies mirroring existing tables)
Pending action: apply to EndoCareDB via Supabase SQL editor or `supabase db push`. Code relies on it — order matters (deploy code AFTER applying migration).

## Verify after deploy
- Schedule a test appointment → should store and appear on dashboard (dashboard now polls every 30s).
- Check Recent Activity populates (was empty due to broken logActivity inserts).
