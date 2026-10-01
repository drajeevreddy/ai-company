# Security Hardening Checklist for PHP + Docker + Apache Apps

## Order of Application (matters for dependencies)
1. **Login rate limiting** — protects auth endpoint first
2. **Session hardening** — cookies only, strict mode
3. **Error suppression** — no leaks to client
4. **CSRF on all mutations** — API + forms
5. **Upload validation** — content + extension
6. **Security headers** — .htaccess mod_headers
7. **Admin noindex** — SEO hygiene
8. **Docker PHP hardening** — ini settings

---

## 1. Login Rate Limiter
**File**: `includes/LoginRateLimiter.php` (new class)
**Wire into**: `admin/login.php` before CSRF check

```php
// In admin/login.php, before CSRF validation:
if (LoginRateLimiter::isBlocked(Helpers::getClientIp())) {
    $remaining = LoginRateLimiter::getRemainingLockSeconds(Helpers::getClientIp());
    $error = "Too many failed attempts. Please try again in {$remaining} seconds.";
}
```

**Storage**: `data/login_attempts.json` (auto-created, git-ignored)
**Policy**: 5 failed attempts → 15 min lockout per IP
**Reset**: `rm data/login_attempts.json` or auto-expiry

---

## 2. Session Hardening
**File**: `includes/bootstrap.php`

```php
if (session_status() === PHP_SESSION_NONE) {
    session_name(SESSION_NAME);
    $secure = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off');
    ini_set('session.use_strict_mode', '1');
    ini_set('session.use_only_cookies', '1');
    ini_set('session.cookie_httponly', '1');
    ini_set('session.cookie_secure', $secure ? '1' : '0');
    ini_set('session.cookie_samesite', 'Lax');
    ini_set('session.gc_maxlifetime', '1440'); // 24 min
    session_set_cookie_params([
        'lifetime' => 1440,
        'path' => '/',
        'domain' => '',
        'secure' => $secure,
        'httponly' => true,
        'samesite' => 'Lax',
    ]);
    session_start();
}
```

---

## 3. Error Suppression (Production)
**File**: `config/config.php` (after timezone)

```php
// Production-safe error handling: log everything, never leak to client.
ini_set('display_errors', '0');
ini_set('log_errors', '1');
@ini_set('error_log', LOG_PATH . '/php-error.log');
```

---

## 4. CSRF on All Mutations
**API endpoints** (add at top, before logic):
```php
if (empty($data['csrf_token']) || !Csrf::validateToken($data['csrf_token'] ?? '')) {
    http_response_code(403);
    echo json_encode(['success' => false, 'message' => 'Invalid or missing CSRF token.']);
    exit;
}
```
- `api/cancel.php`
- `api/reschedule.php`
- (api/book.php already has it)

**Forms** (manage-booking.php):
```php
$csrfToken = Csrf::generateToken();
// In each form:
<input type="hidden" name="csrf_token" value="<?= $csrfToken ?>">
```

---

## 5. Upload Validation
**File**: `includes/Helpers.php` — new method `isValidImageUpload()`

```php
public static function isValidImageUpload(array $file): bool
{
    if ($file['error'] !== UPLOAD_ERR_OK) return false;
    if ($file['size'] > 5 * 1024 * 1024) return false; // 5MB
    $info = getimagesize($file['tmp_name']);
    if (!$info) return false;
    return in_array($info[2], [IMAGETYPE_JPEG, IMAGETYPE_PNG, IMAGETYPE_WEBP], true);
}
```

**Usage** (replace `isValidImage($filename)` checks):
```php
if (Helpers::isValidImageUpload($_FILES['photo'])) { ... }
```

**File**: `uploads/.htaccess` — deny script execution
```apache
<FilesMatch "\.(php|phtml|php3|php4|php5|php7|phar|pl|py|cgi|sh|asp|aspx|jsp)$">
    Order allow,deny
    Deny from all
</FilesMatch>
<FilesMatch "^\.">
    Order allow,deny
    Deny from all
</FilesMatch>
```

---

## 6. Security Headers (.htaccess)
**File**: `.htaccess` (mod_headers block)

```apache
<IfModule mod_headers.c>
    Header set X-Content-Type-Options "nosniff"
    Header set X-Frame-Options "SAMEORIGIN"
    Header set Referrer-Policy "strict-origin-when-cross-origin"
    Header set Permissions-Policy "camera=(), microphone=(), geolocation=(), payment=(), usb=(), interest-cohort=()"
    Header set X-Permitted-Cross-Domain-Policies "none"
    # Remove Server and X-Powered-By (handled by PHP/Apache config)
</IfModule>
```

---

## 7. Admin Noindex
**File**: `admin/partials/header.php`

```html
<meta name="robots" content="noindex, nofollow">
```

---

## 8. Docker PHP Hardening
**File**: `Dockerfile`

```dockerfile
FROM php:8.3-apache
RUN a2enmod rewrite headers

# ZipArchive for admin backup
RUN apt-get update && apt-get install -y --no-install-recommends libzip-dev \
    && docker-php-ext-install zip \
    && rm -rf /var/lib/apt/lists/*

# Production hardening
RUN echo "display_errors=Off"               >> $PHP_INI_DIR/conf.d/hardening.ini \
 && echo "expose_php=Off"                   >> $PHP_INI_DIR/conf.d/hardening.ini \
 && echo "log_errors=On"                    >> $PHP_INI_DIR/conf.d/hardening.ini \
 && echo "error_log=/var/log/php/error.log" >> $PHP_INI_DIR/conf.d/hardening.ini
```

**Apache ServerTokens** (in Dockerfile or apache2.conf):
```dockerfile
RUN echo "ServerTokens Prod" >> /etc/apache2/conf-available/security.conf \
 && echo "ServerSignature Off" >> /etc/apache2/conf-available/security.conf
```

---

## Common Bug Patterns & Fixes (added from session learnings)

### `array_filter()` Preserves Keys → Breaks Numeric Index Access
```php
// BUG: $results = array_filter(...); $first = $results[0]; // fails if first match wasn't index 0
// FIX:
$results = array_values(array_filter(...));
```
Found in `CsvStorage::findAllWhere()` — only Monday (index 0) worked by luck.

### POST Handler After HTML Output → Redirect Fails
**Symptom**: `header('Location: ...')` warning, action doesn't redirect.
**Cause**: `require_once 'partials/header.php'` emits HTML before POST logic.
**Fix**: Move POST handler **before** any `require_once` that outputs HTML.

### Download/Attach Handlers After HTML Output → Broken Downloads
**Symptom**: `?export=1` or `?backup=1` returns HTML page instead of CSV/zip.
**Cause**: Same as above — `header()` calls after HTML output are silently dropped.
**Fix**: Move ALL `isset($_GET['export'])` / `isset($_GET['backup'])` handlers **before** any HTML-emitting `require_once`. Role-gate the handler first, then set headers and exit.

### ZipArchive Missing in Container
**Symptom**: Backup download serves HTML instead of zip.
**Fix**: Add to Dockerfile:
```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends libzip-dev \
    && docker-php-ext-install zip \
    && rm -rf /var/lib/apt/lists/*
```

### Dropdown Menus Cut Off at Viewport Bottom
**Symptom**: Action dropdowns on last table rows open downward and are clipped.
**Cause**: CSS `position: absolute; top: 100%` opens below trigger.
**Fix**: 
- CSS: `.dropdown-menu-bottom { top: auto; bottom: 100%; margin-bottom: 4px; }`
- JS (on click): `const spaceBelow = window.innerHeight - toggle.getBoundingClientRect().bottom; if (spaceBelow < menuHeight + 10) menu.classList.add('dropdown-menu-bottom');`
Verified on appointments.php (7 dropdowns in last rows).

### Analytics Charts in Legacy PHP (No Build Step)
**Solution**: Drop-in Chart.js via CDN:
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<canvas id="monthlyChart" height="120"></canvas>
<script>
const months = <?= json_encode(array_keys($bookingsByMonth)) ?>;
const counts = <?= json_encode(array_values($bookingsByMonth)) ?>;
new Chart(ctx, { type: 'bar', data: { labels: months, datasets: [{ label: 'Appointments', data: counts, backgroundColor: '#3b82f6' }] } });
</script>
```
No build step, works in any PHP admin page.

### Brand/Contact Data Has Multiple Sources — Update All Layers
**Pattern found during Dizi Doc rebrand**:
- Page title → `settings.json` `clinic_name` (index.php reads `$settings['clinic_name'] ?? APP_TITLE`)
- Admin login email → `users.csv` email column
- Contact display → `clinics.csv` clinic_name/phone/email
- WhatsApp links → `clinics.csv` whatsapp column
**Fix**: Grep the variable assignment chain (`$clinicName = $settings['clinic_name'] ?? ...`) and update EVERY layer: `config/settings.json`, `data/clinics.csv`, `data/users.csv`, plus code constants (`APP_NAME`, ICS PRODID/UID, backup filenames). A rename in only one layer silently won't propagate.

### Display Masking Corrupts Data Edits
**Critical**: Terminal/file reads mask sensitive literals (phones, tokens) as `+918****8000`. Copy-pasting masked display writes literal asterisks to disk.
**Fix**: Write contact/credential data with `python3` (exact values) and verify byte-level via fingerprints (length, digit-count, no `*`), never by eye.

---

## Verification Commands (ad-hoc)

```bash
# 1. Lint
docker exec app php -l /var/www/html/config/config.php
docker exec app php -l /var/www/html/includes/Auth.php
# ... all PHP files

# 2. Headers
curl -s -D - -o /dev/null http://localhost:8080/ | grep -iE "x-powered-by|Server:|Permissions-Policy|X-Frame|X-Content|Referrer"

# 3. Protected paths
for p in data/ config/ includes/ logs/; do
  curl -s -o /dev/null -w "%{http_code} " http://localhost:8080/$p; echo
done

# 4. Brute force
# (run verification script template)

# 5. CSRF
curl -s -X POST http://localhost:8080/api/cancel.php --data "booking_id=X&mobile=Y" -w "|%{http_code}"
# expect {"success":false}|403

# 6. Availability clean JSON
curl -s "http://localhost:8080/api/availability.php?doctor=DOC-XXX&date=2026-08-15" | jq .
# no "Warning" or "Fatal" in output
```

---

## Files Modified in This Session (for reference)
- `includes/LoginRateLimiter.php` (new)
- `includes/bootstrap.php` (session hardening)
- `config/config.php` (error suppression)
- `admin/login.php` (rate limiter wired)
- `api/cancel.php` (CSRF)
- `api/reschedule.php` (CSRF)
- `manage-booking.php` (CSRF on all forms)
- `includes/Helpers.php` (isValidImageUpload)
- `uploads/.htaccess` (new, deny scripts)
- `.htaccess` (security headers)
- `admin/partials/header.php` (noindex)
- `Dockerfile` (zip + PHP hardening)
- `admin/settings.php` (backup handler moved before output)
- `admin/appointments.php` (POST handler before output)
- `data/schedules.csv` (hourly slots, cap=3)
- `data/clinics.csv` (Dizi Doc, new phone/email)
- `data/users.csv` (admin email = owner@example.com)
- `config/settings.json` (clinic_name = Dizi Doc)