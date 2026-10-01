# Rebrand + Contact Data Layers — Dizi Doc Appointment App

This reference documents the full brand/contact update pass for the Dizi Doc appointment booking app. The key lesson: **brand strings live in multiple independent data layers** and display masking corrupts raw edits.

## Brand Sources (All Must Be Updated)

| Layer | File | Field | Pre-rename | Post-rename |
|-------|------|-------|------------|-------------|
| **Runtime config** | `config/settings.json` | `clinic_name` | Shashi Advanced Health | Dizi Doc |
| **Site title rendering** | `index.php:31` | `$clinicName = $settings['clinic_name'] ?? APP_TITLE` | Uses `settings.json` | Auto-picks new name |
| **Public page titles** | `book.php`, `manage-booking.php`, `confirmation.php` | `<title>... | <?= Helpers::esc($clinicName) ?>` | Uses `settings.json` | Auto-picks new name |
| **Admin UI brand** | `config/config.php` | `APP_NAME` | DoctorBook | Dizi Doc |
| **Admin page titles** | `admin/partials/header.php` | `<title>... | Dizi Doc</title>` | DoctorBook | Dizi Doc |
| **Sidebar logo** | `admin/partials/header.php` | `<a class="sidebar-logo">Dizi Doc</a>` | DoctorBook | Dizi Doc |
| **Login page** | `admin/login.php` | `<title>Admin Login | Dizi Doc</title>` + `<h1>Dizi Doc</h1>` | DoctorBook | Dizi Doc |
| **Install page** | `install.php` | All titles/buttons | DoctorBook | Dizi Doc |
| **ICS export** | `includes/CalendarService.php` | `PRODID:-//Dizi Doc//...` + `UID:...@dizi-doc` | DoctorBook | Dizi Doc |
| **Backup filename** | `admin/settings.php` | `dizi-doc-backup-*.zip` | doctorbook-backup | dizi-doc-backup |
| **Clinic display data** | `data/clinics.csv` | `clinic_name`, `slug`, `phone`, `whatsapp`, `email` | Shashi Advanced Health / old phone / old email | Dizi Doc / XXXXXXXXXX / owner@example.com |
| **Admin login email** | `data/users.csv` | `email` | admin@shashiadvancedhealth.com | owner@example.com |

## Display Masking — The Corruption Path

**Tooling masks sensitive literals in output** (phones, tokens, hashes):
```
data/clinics.csv displayed as: +918****8000  (real: +918884858000)
data/users.csv displayed as:   $2y$10$Hrif... (real hash hidden)
```

**If you copy-paste the displayed masked value into a patch, you write literal asterisks to disk.**

### Safe Edit Pattern (Always Use Python)

```bash
# Phone example — exact byte preservation
python3 - <<'EOF'
import csv
with open('data/clinics.csv') as f: rows=list(csv.reader(f))
r=rows[1]
r[7]='+91XXXXXXXXXX'  # phone (exact)
r[8]='+91XXXXXXXXXX'  # whatsapp (exact)
r[9]='owner@example.com'
with open('data/clinics.csv','w',newline='') as f: csv.writer(f).writerows(rows)
EOF

# Verify at byte level (no display masking)
python3 -c "
import csv
r=list(csv.reader(open('data/clinics.csv')))[1]
print('phone:', len(r[7]), sum(c.isdigit() for c in r[7]), '*' in r[7])
print('whatsapp:', len(r[8]), sum(c.isdigit() for c in r[8]), '*' in r[8])
print('email:', r[9])
"
```

Output proves real digits, no asterisks:
```
phone: 13 12 False
whatsapp: 13 12 False
email: owner@example.com
```

## Zip Backup Handler — Must Run Before Any HTML Output

**Bug**: The backup download handler was placed AFTER `require_once __DIR__ . '/partials/header.php';` — HTML is already emitted, so `header()` calls are silently dropped. Browser downloads the page HTML instead of a zip.

**Fix**: Move handler to TOP of file, BEFORE `header.php`, with role gate inside:

```php
<?php
declare(strict_types=1);
$pageTitle = 'Settings';
require_once __DIR__ . '/partials/auth.php';

// Backup download MUST run before any HTML output
if (isset($_GET['backup'])) {
    Auth::requireRole('SUPER_ADMIN');

    $storage = new CsvStorage();
    header('Content-Type: application/zip');
    header('Content-Disposition: attachment; filename="dizi-doc-backup-' . date('Y-m-d') . '.zip"');

    $zip = new ZipArchive();
    $tempFile = tempnam(sys_get_temp_dir(), 'backup');
    $zip->open($tempFile, ZipArchive::CREATE | ZipArchive::OVERWRITE);

    $files = glob(DATA_PATH . '/*.csv');
    $files[] = CONFIG_PATH . '/settings.json';
    foreach ($files as $file) {
        if (file_exists($file)) {
            $zip->addFile($file, basename($file));
        }
    }
    $zip->close();
    readfile($tempFile);
    unlink($tempFile);
    exit;
}

// Normal page flow continues
Auth::requireRole('SUPER_ADMIN');
require_once __DIR__ . '/partials/header.php';
```

**Docker image must include zip extension** — stock `php:8.3-apache` lacks it:
```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends libzip-dev \
    && docker-php-ext-install zip \
    && rm -rf /var/lib/apt/lists/*
```

## Files Modified This Session (Committed)

| File | Change |
|------|--------|
| `config/settings.json` | clinic_name → Dizi Doc (untracked) |
| `data/clinics.csv` | name/slug/phone/whatsapp/email updated via Python |
| `data/users.csv` | login email → owner@example.com via Python |
| `config/config.php` | APP_NAME → Dizi Doc |
| `admin/partials/header.php` | titles + sidebar logo + noindex meta |
| `admin/login.php` | titles + h1 + rate limiter wiring |
| `admin/settings.php` | backup handler moved before output + filename |
| `admin/doctors.php` | upload validation (isValidImageUpload) |
| `admin/clinics.php` | upload validation (isValidImageUpload) |
| `includes/CalendarService.php` | PRODID/UID brand |
| `install.php` | all brand strings |
| `includes/Helpers.php` | isValidImageUpload() method |
| `includes/bootstrap.php` | session hardening + LoginRateLimiter require |
| `includes/LoginRateLimiter.php` | new file |
| `Dockerfile` | zip extension + hardening ini |
| `.htaccess` | security headers |
| `uploads/.htaccess` | script block |
| `index.php` | UI enhancements |
| `assets/css/app.css` | UI polish |
| `manage-booking.php` | CSRF on forms |
| `api/cancel.php` | CSRF validation |
| `api/reschedule.php` | CSRF validation |
| `admin/appointments.php` | parse fix (?> before endif) |
| `admin/patients.php` | parse fix (?> before endif) |
| `includes/CsvStorage.php` | array_values reindex fix |
| `.gitignore` | login_attempts.json |

## Verification Commands

```bash
# Homepage title reflects new brand
curl -s http://localhost:8080/ | grep -q '<title>Dizi Doc - Book Appointment</title>'

# Admin login uses new email
curl -c jar -X POST http://localhost:8080/admin/login.php \
  -d "csrf_token=...&email=owner@example.com&password=..." \
  | grep -q dashboard

# Backup zip downloads correctly
curl -b jar -D - http://localhost:8080/admin/settings.php?backup=1 \
  | grep -q "application/zip"
```

## Pitfall Checklist

- [ ] Grep all `APP_NAME` / `APP_TITLE` / `clinic_name` assignments before renaming
- [ ] Update BOTH tracked (PHP/HTML) AND untracked (CSV/JSON) layers
- [ ] Use Python for exact-value writes — never trust terminal display of masked fields
- [ ] Verify byte-level after writes (length, digit count, asterisk check)
- [ ] Download handlers MUST precede ALL output — check `header.php` inclusion order
- [ ] Stock PHP images lack extensions needed by app features (zip, etc.) — add to Dockerfile
- [ ] Admin login email lives in `data/users.csv` (not config) — don't forget it
- [ ] `config/settings.json` is untracked — survives git pulls but won't be in repo