# Migration 00008: Clinic Isolation RLS Policies

## Purpose
Fix cross-clinic data leakage by enforcing clinic-level Row Level Security on all tables.

## Trigger
Applied after discovering clinic_admin users could see ALL clinics' data because:
1. RLS policies only checked roles (doctor, clinic_admin, etc.) — no clinic_id filter
2. `queries.ts` used admin client (service-role key) which bypasses RLS entirely

## Migration Content
See `supabase/migrations/00008_clinic_isolation_rls.sql` for full SQL.

Key additions:
- `get_user_clinic_ids()` helper function — returns clinic IDs for current user via `clinic_staff` table
- Clinic-isolated RLS policies on ALL tables: patients, appointments, soap_notes, prescriptions, invoices, lab_orders, hba1c_records, activity_logs, allergies, medical_history, timeline, blood_sugar_logs, diabetes_assessments, lab_tests, clinics, clinic_staff, queue, prescription_items, invoice_items, payments, lab_results
- Storage bucket policies for patient_documents, lab_reports, prescriptions — clinic-isolated
- `super_admin` bypasses clinic isolation; `clinic_admin` sees only their clinic(s)

## Apply to Live Supabase
1. Go to Supabase Dashboard → SQL Editor
2. Paste contents of `supabase/migrations/00008_clinic_isolation_rls.sql`
3. Run

## Verify After Apply
- Create test user in Clinic A
- Create test user in Clinic B
- Each should only see their clinic's patients/appointments
- Recent Activity should show only their clinic's data
- Dashboard metrics should reflect only their clinic's data

## Code Changes Required After Migration
After applying migration, `queries.ts` MUST be refactored to use regular client (not admin):
```ts
// Before (bypasses RLS - data leak)
function getDb() { return createAdminClient(); }

// After (respects RLS)
async function getDb() { return await createClient(); }

// All call sites: getDb().from(...) → const db = await getDb(); db.from(...)
```