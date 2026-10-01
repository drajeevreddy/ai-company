---
name: supabase-nextjs-debugging
description: Debug write/storage failures in Supabase Next.js apps.
---

# Supabase + Next.js Data-Layer Debugging

When a user reports "X doesn't get stored", "dashboard doesn't update", or "silently nothing happens" in a Next.js app backed by Supabase (a queries module + SQL migrations), work this checklist in order BEFORE touching UI code.

## Root causes (check in this order)

### 1. Error-swallowing query helper (most common)
A `safeQuery(fn, fallback)` that try/catches and returns a fallback makes EVERY write failure silent: UI shows success, row never lands. Fix: add a sibling write helper that propagates errors:
```ts
async function writeQuery<T>(fn: () => Promise<T>, _fallback?: T | null): Promise<T> {
  return await fn(); // errors bubble to caller's try/catch → real error toast
}
```
Mechanical conversion is safe: same 2-arg signature, so only swap `return safeQuery(async () => {` → `return writeQuery(async () => {` inside WRITE functions (reads keep safeQuery for graceful empty states). Verify with `grep -c "safeQuery(async"` vs `grep -c "writeQuery(async"`.

### 1b. Admin client bypassing RLS (data leak)
A `getDb()` that returns `createAdminClient()` (service-role key) bypasses ALL Row Level Security policies. Every read/write runs as superuser — users see ALL clinics' data, not just their own.
Fix: switch to regular client:
```ts
async function getDb() {
  // Use regular client (respects RLS) for all operations.
  // Admin client bypasses RLS and causes data leakage.
  return await createClient(); // anon key + session cookies
}
```
Then fix all call sites: `getDb().from(...)` → `const db = await getDb(); db.from(...)`.
This requires adding `const db = await getDb();` at the start of each function that uses the DB, then using `db.from(...)` throughout. For large codebases, do this with a proper AST transformation (not regex) — regex breaks on multi-line calls and nested parens.

### 2. Schema-vs-code mismatches
Diff every column the code inserts/selects against the actual migrations:
- NOT NULL columns with no default (e.g. `start_time`, `end_time`) → every insert fails "null value in column ...". Fix: populate in code AND/OR `ALTER COLUMN ... SET DEFAULT` in a new migration.
- CHECK constraints rejecting UI values — usually case/format mismatch ("Consultation" vs 'consultation', "New Patient", "Follow-up"). Fix: normalize in code (map to constrained lowercase values) AND drop/relax the constraint in a migration.
- Enums missing values the code writes ('rescheduled', 'checked_in' not in the status enum/CHECK). Use only valid enum values; extend the enum via migration only if the UI genuinely needs the new state.
- Columns that don't exist (prescriptions.status vs is_active; activity_logs.user_name vs user_id + REQUIRED resource_type). Grep every insert column against the migration.
- Tables referenced in code but never created by any migration (medicines, scheduled_reminders, ...). Compare `grep -rn '.from("' src/lib/queries.ts` against `grep -h "CREATE TABLE" supabase/migrations/*.sql`. A migration that only ALTERs an existing table is a giveaway the CREATE TABLE is missing.

### 3. UTC date bugs (India/IST apps)
`new Date().toISOString().split("T")[0]` is UTC — in timezones ahead of UTC it shifts "today" back a day. Same bug hits month-end: `new Date(y, m, 0).toISOString()` returns the PREVIOUS day for IST, dropping the last day of the month from month views. Use a local date-key helper:
```ts
function localDateKey(d: Date = new Date()) {
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,"0")}-${String(d.getDate()).padStart(2,"0")}`;
}
```

### 4. Broken FK display joins
Rows store denormalized `patient_name` but the UI renders `item.patients?.first_name` → "Unknown" everywhere. Fix: `item.patient_name || (item.patients ? `${item.patients.first_name} ${item.patients.last_name}` : "Unknown")` and add the optional field to the local interface.

### 5. Dashboard "not updating"
Usually a consequence of (1)+(2): writes fail silently so metrics never change. Also audit the metrics query itself (selecting `invoices.amount` when the column is `total`; no date filter; `status_text` vs enum `status`). Add client auto-refresh (poll every ~30s) so new rows appear without manual reload.

### 6. Custom Dialog component overlaps footer buttons (z-index / layout)
A custom `Dialog` (not Radix) renders inline when `open=true`. If the content wrapper is a plain `div` with `space-y-4`, a full-width `<label>` in the form body can overlap the footer (`DialogFooter`) because both are `position: relative` with `z-index: auto`. The `<label class="block">` spans the full dialog width and intercepts clicks on the "Schedule" button.
Fix: make the dialog content a **flex column** so footer is structurally separated:
```tsx
<div className="flex flex-col">
  <header className="shrink-0 border-b p-4">...</header>
  <div className="flex-1 overflow-y-auto p-4">{children}</div>
  <footer className="shrink-0 mt-4 pt-4 border-t">...</footer>
</div>
```
Also ensure the footer's `DialogFooter` has `shrink-0` (and optionally `z-10` for safety).

## Verification workflow
- `npm install` first, then `npx tsc --noEmit` (exit 0 = clean).
- `npm run build` — pages importing the Supabase client throw at prerender WITHOUT env vars. Create a **gitignored** `.env.local` with placeholder `NEXT_PUBLIC_SUPABASE_URL` / `NEXT_PUBLIC_SUPABASE_ANON_KEY` / `SUPABASE_SERVICE_ROLE_KEY` just for the build, delete it after. (Same pattern as vercel-deployment-troubleshooting: static generation requirement, not a runtime env issue.)
- `npm run lint` — see vercel-deployment-troubleshooting for the eslint flat-config setup (`next lint` is deprecated and interactive).

## Pitfalls
- PostgREST casts `'HH:MM'` string literals to TIME columns fine on insert — no cast needed.
- Some tables use `is_active` bool with NO `status` column — render status in UI from is_active.
- Once writes throw, ensure pages wrap them in try/catch (most already do) so failures surface as error toasts.
- Write migration constraints defensively: `DROP CONSTRAINT IF EXISTS <table>_<col>_check` (Postgres auto-names CHECKs `{table}_{column}_check`).

## References
- references/doccare-endocare.md — worked example: EndoCare/doccare app (repo drajeevreddy/doccare), every bug found + fix applied, migration 00007 + 00008 contents.
- references/dialog-flex-column-fix.md — custom Dialog component z-index / layout fix for footer button overlap.