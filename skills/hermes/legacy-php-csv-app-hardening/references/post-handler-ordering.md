# Moving POST/Export Handlers Before HTML Output

## Problem
PHP `header()` calls fail with "Cannot modify header information - headers already sent" when any HTML output has already been emitted. In this codebase, `require_once __DIR__ . '/partials/header.php'` emits HTML immediately, so any `header('Location: ...')` or CSV export headers after that point fail silently or produce corrupted output.

## Pattern
Move ALL header-requiring logic BEFORE `require_once header.php`:

```php
// BEFORE (broken)
require_once __DIR__ . '/partials/header.php';

if ($_POST['action'] === 'confirm') {
    header('Location: appointments.php'); // FAILS - HTML already sent
    exit;
}

// AFTER (fixed)
require_once __DIR__ . '/partials/auth.php';

// Handle POST BEFORE any HTML
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['action'])) {
    if (!Csrf::validateToken($_POST['csrf_token'] ?? '')) {
        Helpers::setFlash('error', 'Invalid security token.');
    } else {
        // ... handle action ...
        header('Location: appointments.php');
        exit;
    }
}

// Handle CSV export BEFORE any HTML
if (isset($_GET['export'])) {
    header('Content-Type: text/csv');
    header('Content-Disposition: attachment; filename="..."');
    // ... output CSV ...
    exit;
}

require_once __DIR__ . '/partials/header.php'; // HTML starts HERE
```

## Files Fixed in This Session
- `admin/appointments.php` — POST actions (confirm/cancel/complete/noshow) + CSV export
- `admin/patients.php` — CSV export
- `admin/settings.php` — Zip backup download

## Result
- Redirects work (HTTP 302 → 200 on target)
- CSV exports download with correct `Content-Type: text/csv`
- Zip backups download with correct `application/zip` headers
- No "headers already sent" warnings in php-error.log