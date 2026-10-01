---
name: supabase-app-fixes
description: Fix Supabase apps with silent write failures.
---

# Supabase App Fixes (silent write failures / stale dashboards)

## When to use
- User reports "data doesn't get stored", "dashboard doesn't update", "form says saved but nothing appears".
- App is Next.js (or any framework) + Supabase (PostgREST), typically hosted on Vercel/Render with a hosted Supabase project.
- You are about to diff application code against SQL migrations (`supabase/migrations/`).

## Core diagnostic sequence
1. Clone, read `package.json`, list migrations, and locate the data-access layer (usually `src/lib/queries.ts` — often "use server" server actions using an admin/service-role client).
2. Cross-check every `.from("table")` call in code against which migration creates that table. Missing tables are a top cause: migrations sometimes ALTER a table that is never created anywhere (e.g. a migration adding columns to `medicines` with no CREATE TABLE for it).
3. For every INSERT/UPDATE payload in code, verify against the CREATE TABLE:
   - NOT NULL columns with no default → insert fails: "null value in column X".
   - CHECK constraints vs UI values → casing ("Consultation" vs 'consultation') or missing value ("checked_in" not in queue status CHECK).
   - Postgres enum values → status 'rescheduled' not in appointment_status enum.
   - Columns that don't exist at all → activity_logs.user_name, prescriptions.status.
4. Find the error-swallowing wrapper FIRST — it is why the bugs stayed invisible.

## The silent-success pattern (most important)
Data layers often wrap every query in try/catch and return a fallback (e.g. `safeQuery(fn, fallback)`). Reads benefit (empty array instead of crash), but WRITES silently return `null` on error → the caller's `await createAppointment(...)` never throws → toast "Appointment scheduled!" while zero rows were inserted.

Fix: two helpers —
- `safeQuery(fn, fallback)` for reads (swallow, fall back).
- `writeQuery(fn, _fallback?)` for mutations: just `return await fn()` so errors PROPAGATE and the caller's try/catch + toast shows the real DB error.

Mechanical conversion: a small Python script that walks function spans and replaces `return safeQuery(async () => {` → `return writeQuery(async () => {` only inside write functions (reads keep safeQuery). Do NOT global-replace. Afterwards, verify every converted write function's callers already have try/catch (most pages do) — otherwise you introduce unhandled rejections.

## Fix checklist per failure class
| Class | Symptom | Code fix | DB fix (new migration) |
|---|---|---|---|
| NOT NULL no default | insert fails | supply value (derive start_time/end_time from a single time input) | ALTER COLUMN ... SET DEFAULT |
| CHECK rejects UI value | insert fails | normalize to valid values ("Follow-up"→"follow_up", "New Patient"→"consultation") | DROP CONSTRAINT IF EXISTS + re-add relaxed |
| enum value invalid | update fails | use a valid enum value, or stop tracking that state in the enum | extend the enum |
| nonexistent column | insert fails | match schema (prescriptions.status → is_active) | — |
| missing table | query/insert fails | — | CREATE TABLE IF NOT EXISTS in new migration |

## Migration pattern for an already-deployed DB
- Add `supabase/migrations/000NN_fixes.sql`, fully idempotent:
  - `ALTER TABLE ... ALTER COLUMN x SET DEFAULT '...';` (keeps NOT NULL, fixes old inserts)
  - `ALTER TABLE ... DROP CONSTRAINT IF EXISTS <table>_<column>_check;` then re-add with the extended IN list. Postgres auto-names CHECK constraints `<table>_<column>_check`.
  - `CREATE TABLE IF NOT EXISTS ...` for every referenced-but-missing table, with matching RLS enable + policies if the app uses the anon key.
- User applies via Supabase SQL Editor or `supabase db push`. Normalize values in BOTH code and migration (belt & suspenders) so legacy rows / old app versions never block saves.

## Timezone bugs (India / any UTC+ zone app)
- `new Date().toISOString().split("T")[0]` is UTC: between local midnight and ~05:29 IST, "today" is still yesterday UTC → dashboards show the wrong day.
- `new Date(y, m, 0).toISOString()` for month-end shifts the last day back one → month view misses the 30th/31st.
- Fix: local-time formatter (`getFullYear/getMonth+1/getDate` padded) — one `localDateKey()` helper reused in queries AND pages.

## Denormalized data vs FK joins
- App stores `patient_name` (denormalized text) but the UI joins `patients(first_name,last_name)` → join is null → "Unknown" / "undefined undefined" everywhere.
- Fix UI with fallback: `row.patient_name || (row.patients ? \`${first} ${last}\` : "Unknown")` and add `patient_name?: string` to the row interfaces (TypeScript will demand it).

## Dashboard "doesn't update"
- Root cause is usually the writes failing (above) — fix those first, then add polling.
- Add auto-refresh: `setInterval(load, 30000)` inside useEffect with cleanup.
- Check metric queries for wrong columns: `select("amount")` on invoices where the column is `total`; missing date filter; filtering on the wrong status column (`status` enum vs `status_text` compat column).

## Verification without env keys
- Next.js prerender fails without `NEXT_PUBLIC_SUPABASE_URL`: build error "@supabase/ssr: Your project's URL and API key are required to create a Supabase client!".
- Fix: create gitignored `.env.local` with placeholder values → `npm run build` passes → remove it after verifying. It is NOT a code error.
- Run `npx tsc --noEmit` first (fast, catches interface/type breaks).
- `next lint` (Next 15) is deprecated and opens an interactive setup prompt when no ESLint config exists → exits 1 on the prompt, not on lint errors. Don't auto-generate a config unless asked.

## Pitfalls
- Service-role/admin clients bypass RLS — RLS policies are usually NOT the cause of failing server actions; check constraints and columns first.
- `count(*) + 1` is the wrong way to issue queue/token numbers (completed rows inflate the count) — use `max(token_number) + 1`.
- Keep migration fixes minimal and idempotent; do not rewrite the whole schema.
- When fixing a write that also affects display state (e.g. check-in), sync the related row (appointment status) so badges/lists reflect the action.

## References
- references/doccare-endocare.md — worked example: EndoCare (doccare) Next.js 15 + Supabase app; full bug list, exact fixes, and deployment steps.