# Admin Client Bypass Pattern — Detection & Fix

## Problem
`getDb()` returning `createAdminClient()` (service-role key) bypasses ALL RLS policies.
Users see ALL data across ALL clinics — total data leak.

## Detection
```bash
# Search for admin client usage in queries layer
grep -n "createAdminClient" src/lib/queries.ts
grep -n "getDb()" src/lib/queries.ts | head -5
```

## Fix Pattern

### 1. Switch to regular client
```typescript
// Before
function getDb() { return createAdminClient(); }

// After
async function getDb() {
  return await createClient(); // anon key + session cookies
}
```

### 2. Fix all call sites
```typescript
// Before: getDb().from("table")...
const { data } = await getDb().from("patients").select("*");

// After
const db = await getDb();
const { data } = await db.from("patients").select("*");
```

### 3. Bulk fix for large codebases
Use an AST transformer (not regex):
- Parse each function
- Add `const db = await getDb();` after opening brace
- Replace `getDb().` with `db.` within function scope

## Verify
```bash
# No more admin client in queries
grep -c "createAdminClient" src/lib/queries.ts
# Should be 0 (or only in server.ts for admin endpoints)

# All DB calls go through regular client
grep "getDb()" src/lib/queries.ts | grep -v "await getDb"
```