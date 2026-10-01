# CSV array_filter Key Preservation Bug

## Problem
`CsvStorage::findAllWhere()` uses `array_filter()` which **preserves array keys**. When filtering a CSV array:

```php
// Original: [0 => row1, 1 => row2, 2 => row3]
// After array_filter matching row2: [1 => row2]
// Code expects $results[0] → misses, gets PHP warning, corrupts JSON
```

Only the first row (index 0) worked by luck. Monday bookings worked because their schedule was at index 0.

## Fix
Wrap the filtered result in `array_values()` to re-index:

```php
public function findAllWhere(string $table, array $conditions): array
{
    $data = $this->readAll($table);
    $filtered = array_filter($data, function($row) use ($conditions) {
        foreach ($conditions as $key => $value) {
            if (($row[$key] ?? '') !== $value) return false;
        }
        return true;
    });
    return array_values($filtered); // <-- KEY FIX
}
```

## Verification
- Availability API returns clean JSON for all weekdays (Mon–Thu capacities 4,4,5,5)
- No PHP warnings in response body
- Monday/Tuesday/Wednesday/Thursday all work correctly

## Lesson
Never assume `array_filter()` returns 0-indexed array. Always `array_values()` when numeric index matters.