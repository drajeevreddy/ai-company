# CsvStorage array_filter() Key-Preservation Bug — The Silent Duplicate/Capacity Bypass

## The Bug

`CsvStorage::findAllWhere()` (and any PHP row-store using `array_filter()` directly) preserves original array keys. When filtering a multi-row CSV:

```php
// Original:  [0 => monday, 1 => tuesday, 2 => wednesday]
$filtered = array_filter($all, fn($r) => $r['day'] === 'Tuesday');
// Result:    [1 => tuesday]    ← KEY 1, NOT 0!
```

Downstream code indexing `$results[0]` gets `null` → **silent failures** in:
- **Duplicate detection**: `checkDuplicate()` uses `findWhere` → returns null for non-first-row matches → **second booking for same slot succeeds** (double bookings silently allowed).
- **Availability lookups**: `AvailabilityEngine::getAvailableSlots()` calls `findAllWhere` on schedules; non-first-row days (Tue–Fri) had no key 0 → PHP `Undefined array key 0` warnings leaked into JSON responses, corrupting client parsing AND the duplicate check silently failed.
- **Any `findWhere()` call** expecting the first filtered row.

## Fix Applied

```php
// In CsvStorage::findAllWhere()
return array_values(array_filter($all, $predicate));
```

`array_values()` re-indexes 0..N-1 so `$results[0]` is always the first match.

## Verification (Must Run)

```bash
# 1. API returns CLEAN JSON (no Warning/Fatal lines)
curl -s "http://localhost:8080/api/availability.php?doctor=DOC-BE6FDE5A&date=2026-08-12" | grep -E 'Warning|Fatal' && echo FAIL || echo OK

# 2. Duplicate booking REJECTED (capacity=3, book twice same slot → 400)
# 3. Availability for Tue/Wed/Thu/Fri works (was silently broken before)
# 4. After fix: Mon–Fri all show 8 hourly slots, capacity 3 each
```

## Root Cause Pattern

**Any row-store layer** in PHP that filters with `array_filter`/`array_map`/`preg_grep` **must `array_values()` before consumers index `[0]`**. The bug is silent — no crash, just wrong data returned — so the ONLY proof is E2E reject-path testing (duplicate → 400, capacity→0).

## Files Touched

- `includes/CsvStorage.php` — `findAllWhere()` + `array_values()` wrapper (committed)
- `includes/AvailabilityEngine.php` — consumer of `findAllWhere()` (verified fixed by E2E)
- `includes/BookingEngine.php` — `checkDuplicate()` consumer (verified fixed by E2E)