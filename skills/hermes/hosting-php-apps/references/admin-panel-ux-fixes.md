# Admin Panel UX Fixes — Export Handlers, Chart.js, POST Handler Ordering

## The Core Pattern: Header/Output Handlers Must Precede ALL HTML

Multiple admin pages had the same bug: export/backup handlers placed AFTER `require_once header.php;` — HTML already emitted, so `header()` calls silently drop. User downloads HTML instead of CSV/zip.

### Files Fixed

| File | Handler | Symptom Before | Fix |
|------|---------|----------------|-----|
| `admin/appointments.php` | `?export=1` CSV | HTML page downloaded | Move handler before `header.php` |
| `admin/patients.php` | `?export=1` CSV | HTML page downloaded | Move handler before `header.php` |
| `admin/settings.php` | `?backup=1` Zip | HTML page downloaded | Move handler before `header.php` + role gate inside |
| `admin/appointments.php` | POST actions (confirm/cancel/etc) | `header('Location')` silent fail | Move before `header.php` |

### Correct Ordering Template

```php
<?php
declare(strict_types=1);
$pageTitle = 'Page Title';
require_once __DIR__ . '/partials/auth.php';

// 1. ALL handlers that emit headers (exports, downloads, POST redirects)
//    MUST run BEFORE any HTML output.
if (isset($_GET['export'])) { /* CSV headers + exit */ }
if (isset($_GET['backup'])) { /* Zip headers + exit */ }
if ($_SERVER['REQUEST_METHOD'] === 'POST') { /* action + header('Location') + exit */ }

// 2. THEN include header.php (emits <html>...)
require_once __DIR__ . '/partials/header.php';

// 3. Normal page rendering continues...
?>
```

## Analytics Chart.js Integration

Analytics page had tabular data but no visual charts. Added Chart.js via CDN:

```php
// In the Monthly Trend card body (replacing the bar-table):
<canvas id="monthlyChart" height="120"></canvas>

// After footer include:
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<script>
if (typeof Chart !== 'undefined' && document.getElementById('monthlyChart')) {
    const ctx = document.getElementById('monthlyChart').getContext('2d');
    const months = <?= json_encode(array_keys($bookingsByMonth)) ?>;
    const counts = <?= json_encode(array_values($bookingsByMonth)) ?>;
    new Chart(ctx, {
        type: 'bar',
        data: { labels: months, datasets: [{ label: 'Appointments', data: counts, backgroundColor: '#3b82f6' }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } } }
    });
}
</script>
```

## Verification Checklist

- [ ] All admin pages: 200, correct title (Dizi Doc), sidebar nav present
- [ ] `?export=1` → `Content-Type: text/csv` + valid CSV bytes
- [ ] `?backup=1` → `Content-Type: application/zip` + valid zip (unzip -l shows .csv files)
- [ ] POST actions (confirm/cancel/complete/noshow) → 200 redirect + CSV status updated
- [ ] Schedules page (with doctor): Add/Copy/Edit/Delete modals + JS present
- [ ] Analytics: `<canvas id="monthlyChart">` + Chart.js script + data injected
- [ ] No new PHP header warnings in `logs/php-error.log`