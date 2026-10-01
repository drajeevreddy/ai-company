# PHP CSV App Hardening — Complete Pattern (Dizi Doc / appointment app)

This reference captures the full hardening pattern for PHP+CSV appointment/booking apps on Fedora with SELinux Enforcing, Apache in Docker.

---

## 1. Container & Runtime (Fedora Enforcing)

### Dockerfile
```dockerfile
FROM php:8.3-apache

# Routing + headers used by the app (.htaccess)
RUN a2enmod rewrite headers

# Zip backup feature (ZipArchive)
RUN apt-get update && apt-get install -y --no-install-recommends libzip-dev \
    && docker-php-ext-install zip \
    && rm -rf /var/lib/apt/lists/*

# Production hardening: never expose errors/version, tighten session defaults.
RUN echo "display_errors=Off"               >> $PHP_INI_DIR/conf.d/hardening.ini \
 && echo "expose_php=Off"                   >> $PHP_INI_DIR/conf.d/hardening.ini \
 && echo "session.cookie_httponly=1"        >> $PHP_INI_DIR/conf.d/hardening.ini \
 && echo "session.cookie_secure=1"          >> $PHP_INI_DIR/conf.d/hardening.ini \
 && echo "session.cookie_samesite=Lax"      >> $PHP_INI_DIR/conf.d/hardening.ini \
 && echo "session.gc_maxlifetime=1440"      >> $PHP_INI_DIR/conf.d/hardening.ini \
 && echo "session.use_strict_mode=1"        >> $PHP_INI_DIR/conf.d/hardening.ini \
 && echo "session.use_only_cookies=1"       >> $PHP_INI_DIR/conf.d/hardening.ini

# Apache: hide version
RUN echo "ServerTokens Prod"          >> /etc/apache2/conf-enabled/security.conf \
 && echo "ServerSignature Off"        >> /etc/apache2/conf-enabled/security.conf
```

### Run command
```bash
docker run -d \
  --name appointment \
  --restart unless-stopped \
  -p 8080:80 \
  -v /home/painarise/appointment:/var/www/html:z \
  appointment-php:hardened
```

---

## 2. File Ownership Model (Git + Apache Coexistence)

| Path | Owner | Permissions | Purpose |
|------|-------|-------------|---------|
| Tracked PHP/HTML/CSS/JS | host UID 1000 (painarise) | 644 | Git works, Apache reads |
| `data/` `config/` `logs/` `uploads/` | host UID 1000 | **777** | Apache (`www-data`) writes CSV |
| `data/login_attempts.json` | created at runtime | 644 | Brute-force tracking |
| Admin password | **outside repo** at `/home/painarise/appointment_admin_pass.txt` | 600 | Never in git |

**Reset ownership for git pull:**
```bash
docker exec appointment chown -R 1000:1000 /var/www/html
chmod -R 777 data config logs uploads
```

---

## 3. Code-Level Hardening

### Login Rate Limiting (`includes/LoginRateLimiter.php`)
```php
<?php
declare(strict_types=1);

class LoginRateLimiter
{
    private const ATTEMPTS_FILE = __DIR__ . '/../data/login_attempts.json';
    private const MAX_ATTEMPTS = 5;
    private const LOCKOUT_SECONDS = 900; // 15 min

    public static function recordFailure(string $ip): void
    {
        $data = self::load();
        $data[$ip] = ($data[$ip] ?? 0) + 1;
        self::save($data);
    }

    public static function recordSuccess(string $ip): void
    {
        $data = self::load();
        unset($data[$ip]);
        self::save($data);
    }

    public static function isBlocked(string $ip): bool
    {
        $data = self::load();
        return ($data[$ip] ?? 0) >= self::MAX_ATTEMPTS;
    }

    public static function getRemainingLockSeconds(string $ip): int
    {
        // Simplified: always full lockout window after threshold
        return self::LOCKOUT_SECONDS;
    }

    private static function load(): array
    {
        if (!file_exists(self::ATTEMPTS_FILE)) return [];
        $json = file_get_contents(self::ATTEMPTS_FILE);
        return json_decode($json, true) ?? [];
    }

    private static function save(array $data): void
    {
        file_put_contents(self::ATTEMPTS_FILE, json_encode($data));
    }
}
```

### Session Hardening (`includes/bootstrap.php`)
```php
if (session_status() === PHP_SESSION_NONE) {
    session_name(SESSION_NAME);
    $secure = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off');
    ini_set('session.use_strict_mode', '1');
    ini_set('session.use_only_cookies', '1');
    ini_set('session.cookie_httponly', '1');
    ini_set('session.cookie_secure', $secure ? '1' : '0');
    ini_set('session.cookie_samesite', 'Lax');
    ini_set('session.gc_maxlifetime', '1440');
    session_start();
}
```

### Error Handling (`config/config.php`)
```php
// Production-safe error handling: log everything, never leak to the client.
ini_set('display_errors', '0');
ini_set('log_errors', '1');
@ini_set('error_log', LOG_PATH . '/php-error.log');
```

### Admin Login (`admin/login.php`) — key excerpts
```php
// Rate limit check FIRST
if (LoginRateLimiter::isBlocked(Helpers::getClientIp())) {
    $remaining = LoginRateLimiter::getRemainingLockSeconds(Helpers::getClientIp());
    $error = 'Too many failed attempts. Please try again in ' . ceil($remaining / 60) . ' minutes.';
}
elseif (!Csrf::validateToken($_POST['csrf_token'] ?? '')) {
    $error = 'Invalid security token. Please try again.';
}
else {
    $email = trim($_POST['email'] ?? '');
    $password = $_POST['password'] ?? '';
    // ... authenticate ...
    if ($valid) {
        session_regenerate_id(true);  // CRITICAL: session fixation protection
        LoginRateLimiter::recordSuccess(Helpers::getClientIp());
        // ... redirect ...
    } else {
        LoginRateLimiter::recordFailure(Helpers::getClientIp());
        $error = 'Invalid email or password.';
    }
}
```

### Admin Auth Gate (`admin/partials/auth.php`)
```php
<?php
if (!Auth::isLoggedIn()) {
    Helpers::redirect('login.php');
}
Auth::requireRole('SUPER_ADMIN');  // or appropriate role
?>
<meta name="robots" content="noindex, nofollow">
```

### CSRF Coverage (`includes/Csrf.php`)
```php
class Csrf {
    public static function generateToken(): string { /* ... */ }
    public static function validateToken(string $token): bool { /* ... */ }
    public static function field(): string { /* <input hidden> */ }
    public static function metaTag(): string { /* <meta name="csrf-token"> */ }
}
```
Applied to:
- All admin POST forms (`admin/*.php`)
- Public mutation APIs (`api/cancel.php`, `api/reschedule.php`)
- Public manage form: `manage-booking.php`

### Upload Defense
**`uploads/.htaccess`**
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

**`includes/Helpers.php` — image validation**
```php
public static function isValidImageUpload(array $file): bool
{
    $ext = self::getFileExtension($file['name']);
    if (!in_array($ext, ['jpg', 'jpeg', 'png', 'webp'], true)) {
        return false;
    }
    $info = @getimagesize($file['tmp_name']);
    if (!$info || !in_array($info[2], [IMAGETYPE_JPEG, IMAGETYPE_PNG, IMAGETYPE_WEBP], true)) {
        return false;
    }
    return true;
}
```

---

## 4. Header Hardening (Root `.htaccess`)

```apache
# Security headers
<IfModule mod_headers.c>
    Header set X-Content-Type-Options "nosniff"
    Header set X-Frame-Options "SAMEORIGIN"
    Header set Referrer-Policy "strict-origin-when-cross-origin"
    Header set Permissions-Policy "camera=(), microphone=(), geolocation=(), payment=(), usb=(), interest-cohort=()"
    Header set X-Permitted-Cross-Domain-Policies "none"
    Header unset X-Powered-By
    Header always set X-XSS-Protection "1; mode=block"
</IfModule>

# Protect sensitive directories
<DirectoryMatch "^(.*/)?(data|config|includes|logs)/">
    Require all denied
</DirectoryMatch>

# Block .git, .env, etc.
<FilesMatch "^\.">
    Require all denied
</FilesMatch>

# Hide server version
ServerTokens Prod
ServerSignature Off
```

---

## 5. Verification Pattern (Ad-Hoc Scripts)

No canonical test suite exists for PHP/CSV apps. Use this checklist:

```bash
#!/usr/bin/env bash
# verify.sh — run after any hardening change

APP=/home/painarise/appointment
BASE=http://localhost:8080

# 1. PHP lint sweep
for f in $(find "$APP" -name '*.php' -not -path './.git/*'); do
  docker exec appointment php -l "/var/www/html/$f" | grep -q "No syntax errors" || exit 1
done

# 2. Security headers
curl -sI "$BASE/" | grep -qiE "x-powered-by|Server: Apache" && exit 1
curl -sI "$BASE/" | grep -qi "X-Content-Type-Options: nosniff" || exit 1
curl -sI "$BASE/" | grep -qi "X-Frame-Options: SAMEORIGIN" || exit 1
curl -sI "$BASE/" | grep -qi "Referrer-Policy:" || exit 1
curl -sI "$BASE/" | grep -qi "Permissions-Policy:" || exit 1
curl -sI "$BASE/" | grep -qi "X-Permitted-Cross-Domain-Policies: none" || exit 1

# 3. Protected paths
for p in data/ config/ includes/ logs/; do
  [ "$(curl -s -o /dev/null -w "%{http_code}" "$BASE/$p")" = "403" ] || exit 1
done

# 4. Brute-force lockout
# ... (see full script in session)

# 5. CSRF enforcement
curl -s -X POST "$BASE/api/cancel.php" --data "booking_id=X&mobile=X" | grep -q '403' || exit 1

# 6. Admin pages all 200
for p in dashboard.php appointments.php patients.php doctors.php schedules.php clinics.php holidays.php settings.php calendar.php analytics.php; do
  [ "$(curl -s -b $JAR -L -o /dev/null -w "%{http_code}" "$BASE/admin/$p")" = "200" ] || exit 1
done

# 7. Availability API clean JSON
curl -s "$BASE/api/availability.php?doctor=DOC-BE6FDE5A&date=2026-08-12" | grep -q '"success":true' || exit 1

echo "ALL CHECKS PASSED"
```

---

## 6. Common Bugs Found & Fixed

| Bug | Symptom | Fix |
|-----|---------|-----|
| Missing `?>` before `<?php endif; ?>` in admin export blocks | PHP Parse error, 500 on `admin/appointments.php`, `admin/patients.php` | Add `?>` before `<?php endif; ?>` |
| POST handlers running after HTML output | `header('Location:')` fails silently | Move handlers before `require_once header.php` |
| Backup zip download broken | Headers sent before zip handler | Move zip handler before `header.php`, add ZipArchive ext |
| `array_filter()` preserves keys | `$results[0]` misses non-first-row matches | Wrap in `array_values()` in `CsvStorage::findAllWhere()` |
| Missing ZipArchive extension | Fatal error on backup | Add `docker-php-ext-install zip` to Dockerfile |

---

## 7. Mobile Touch Targets (CSS)

```css
.btn { min-height: 52px; }           /* 48px mobile */
.progress-step { min-height: 44px; }  /* 40px mobile */
.doctor-list-item { min-height: 80px; }
.date-card { min-height: 96px; }
.time-slot { min-height: 64px; }
input, select, textarea { font-size: 16px; } /* prevents iOS zoom */
.checkbox-label input { width: 20px; height: 20px; accent-color: var(--color-accent); }

@media (max-width: 768px) {
  .btn { min-height: 48px; }
  .doctor-list-item { min-height: 72px; }
  .date-card { min-height: 84px; }
  .time-slot { min-height: 60px; }
}

@media (max-width: 480px) {
  .btn { min-height: 48px; }
  .date-card { min-height: 84px; }
  .time-slot { min-height: 56px; }
}

/* Touch feedback JS */
document.addEventListener('touchend', () => {}, { passive: true });
document.querySelectorAll('.doctor-list-item, .date-card, .time-slot, .btn').forEach(el => {
  el.addEventListener('touchstart', () => { el.style.opacity = '0.85'; }, { passive: true });
  el.addEventListener('touchend', () => { el.style.opacity = ''; }, { passive: true });
});
```

---

## 8. Design System Integration (Stripe-Inspired)

When redesigning public pages:

```css
:root {
  --color-bg: #ffffff;
  --color-bg-alt: #f8fafc;
  --color-heading: #061b31;        /* Deep navy */
  --color-body: #64748d;           /* Slate */
  --color-label: #273951;
  --color-border: #e5edf5;
  --color-border-strong: #cbd5e1;
  --color-accent: #0d9488;         /* Teal — medical trust */
  --color-accent-hover: #0f766e;
  --color-accent-light: #ccfbf1;
  --color-success: #15be53;
  --color-success-bg: #dcfce7;
  --color-danger: #ea2261;
  --color-danger-bg: #fef2f2;

  --shadow-ambient: rgba(23,23,23,0.06) 0px 3px 6px;
  --shadow-card: rgba(23,23,23,0.08) 0px 15px 35px;
  --shadow-elevated: rgba(50,50,93,0.15) 0px 30px 45px -30px, rgba(0,0,0,0.08) 0px 18px 36px -18px;
  --shadow-focus: 0 0 0 3px rgba(13,148,136,0.3);

  --font-primary: 'Source Sans 3', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
  --font-mono: 'Source Code Pro', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  --font-feature: "ss01";

  --radius-sm: 4px; --radius-md: 6px; --radius-lg: 8px;
}
```

Font import:
```html
<link href="https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@300;400;500;600&family=Source+Code+Pro:wght@400;500;700&display=swap" rel="stylesheet">
```

Apply `font-family: var(--font-primary); font-feature-settings: "ss01"; font-weight: 300;` to headings, `400` to UI.

---

## 9. Complete UI Redesign (Stripe-Inspired, Healthcare-Adapted)

### Pages Redesigned
- `index.php` — Hero, trust bar, feature grid, doctor grid, CTA
- `book.php` — 4-step booking flow (Doctor → Date → Time → Details)
- `confirmation.php` — Success state with WhatsApp/calendar/manage actions

### Design Tokens (Healthcare-Adapted Stripe)
```css
:root {
  --color-bg: #ffffff;
  --color-bg-alt: #f8fafc;
  --color-heading: #061b31;        /* Deep navy — trust, professionalism */
  --color-body: #64748d;           /* Slate — readable body text */
  --color-label: #273951;          /* Dark slate — form labels */
  --color-border: #e5edf5;         /* Soft blue border */
  --color-border-strong: #cbd5e1;  /* Stronger border for focus */
  --color-accent: #0d9488;         /* Teal — medical trust, calm */
  --color-accent-hover: #0f766e;
  --color-accent-light: #ccfbf1;
  --color-success: #15be53;
  --color-success-bg: #dcfce7;
  --color-danger: #ea2261;
  --color-danger-bg: #fef2f2;
  --color-warning: #f59e0b;
  --color-warning-bg: #fef3c7;
  
  /* Shadows — Stripe's blue-tinted multi-layer system adapted */
  --shadow-ambient: rgba(23, 23, 23, 0.06) 0px 3px 6px;
  --shadow-card: rgba(23, 23, 23, 0.08) 0px 15px 35px;
  --shadow-elevated: rgba(50, 50, 93, 0.15) 0px 30px 45px -30px, rgba(0, 0, 0, 0.08) 0px 18px 36px -18px;
  --shadow-focus: 0 0 0 3px rgba(13, 148, 136, 0.3);
  
  /* Typography */
  --font-primary: 'Source Sans 3', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
  --font-mono: 'Source Code Pro', ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  --font-feature: "ss01";
  
  /* Spacing */
  --space-1: 4px; --space-2: 8px; --space-3: 12px; --space-4: 16px;
  --space-5: 20px; --space-6: 24px; --space-8: 32px; --space-10: 40px; --space-12: 48px; --space-16: 64px;
  
  /* Border radius — conservative 4-8px range */
  --radius-sm: 4px; --radius-md: 6px; --radius-lg: 8px;
  
  /* Transitions */
  --transition-fast: 150ms ease; --transition-normal: 200ms ease;
}
```

### Font Import
```html
<link href="https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@300;400;500;600&family=Source+Code+Pro:wght@400;500;700&display=swap" rel="stylesheet">
```

### Key Component Patterns

**Buttons**
```css
.btn {
  display: inline-flex; align-items: center; justify-content: center; gap: var(--space-2);
  padding: 10px 20px; border-radius: var(--radius-md);
  font-family: var(--font-primary); font-feature-settings: var(--font-feature);
  font-size: 16px; font-weight: 400; line-height: 1;
  border: 1px solid transparent; cursor: pointer;
  transition: all var(--transition-fast); text-decoration: none;
  min-height: 44px; /* Touch target */
}
.btn:focus-visible { outline: none; box-shadow: var(--shadow-focus); }
.btn:active { transform: scale(0.98); }

.btn-primary { background: var(--color-accent); color: #fff; border-color: var(--color-accent); }
.btn-primary:hover { background: var(--color-accent-hover); border-color: var(--color-accent-hover); }

.btn-secondary { background: transparent; color: var(--color-accent); border-color: var(--color-border-strong); }
.btn-secondary:hover { background: var(--color-accent-light); border-color: var(--color-accent); }

.btn-ghost { background: transparent; color: var(--color-body); border-color: var(--color-border); }
.btn-ghost:hover { background: var(--color-bg-alt); color: var(--color-heading); }

.btn-block { width: 100%; }
.btn-lg { padding: 14px 28px; font-size: 17px; }
.btn-sm { padding: 8px 16px; font-size: 14px; min-height: 40px; }
```

**Forms**
```css
.form-group { margin-bottom: var(--space-5); }
.form-group label {
  display: block; font-family: var(--font-primary); font-feature-settings: var(--font-feature);
  font-size: 14px; font-weight: 400; color: var(--color-label); margin-bottom: var(--space-2);
}
.form-group input, .form-group select, .form-group textarea {
  width: 100%; padding: 12px 14px;
  border: 1px solid var(--color-border); border-radius: var(--radius-md);
  font-family: var(--font-primary); font-feature-settings: var(--font-feature);
  font-size: 16px; line-height: 1.5; color: var(--color-heading); background: var(--color-bg);
  transition: all var(--transition-fast);
}
.form-group input:focus, .form-group select:focus, .form-group textarea:focus {
  outline: none; border-color: var(--color-accent); box-shadow: var(--shadow-focus);
}
```

**Touch Targets (Mobile)**
```css
/* Minimum 44px touch targets everywhere */
.btn { min-height: 52px; }           /* 48px mobile */
.progress-step { min-height: 44px; }  /* 40px mobile */
.doctor-list-item { min-height: 80px; }
.date-card { min-height: 96px; }
.time-slot { min-height: 64px; }
input, select, textarea { font-size: 16px; } /* Prevents iOS zoom */
.checkbox-label input { width: 20px; height: 20px; accent-color: var(--color-accent); }

/* Responsive touch targets */
@media (max-width: 768px) {
  .btn { min-height: 48px; }
  .doctor-list-item { min-height: 72px; }
  .date-card { min-height: 84px; }
  .time-slot { min-height: 60px; }
}

@media (max-width: 480px) {
  .btn { min-height: 48px; }
  .date-card { min-height: 84px; }
  .time-slot { min-height: 56px; }
}
```

**Touch Feedback JS**
```javascript
// Prevent double-tap zoom on iOS
document.addEventListener('touchend', () => {}, { passive: true });

// Improve touch feedback for interactive elements
document.querySelectorAll('.doctor-list-item, .date-card, .time-slot, .btn, .time-slot-sm').forEach(el => {
  el.addEventListener('touchstart', function() {
    this.style.opacity = '0.85';
  }, { passive: true });
  el.addEventListener('touchend', function() {
    this.style.opacity = '';
  }, { passive: true });
});
```

---

## 10. Booking Flow UX (4-Step Wizard)

### Step Structure
1. **Doctor** — Card list with photo, name, specialty, qualifications
2. **Date** — Horizontal scrollable date cards (today/tomorrow labels)
3. **Time** — Vertical time-slot cards with capacity/remaining
4. **Details** — Summary card + name, mobile, age, gender, email, reason, consent

### Progress Indicator
```css
.progress-steps {
  display: flex; justify-content: center; gap: var(--space-3); margin-bottom: var(--space-8);
}
.progress-step {
  display: flex; flex-direction: column; align-items: center; gap: var(--space-1);
  padding: var(--space-3) var(--space-4); border-radius: 9999px;
  font-family: var(--font-primary); font-feature-settings: var(--font-feature);
  font-size: 13px; font-weight: 400; color: var(--color-body);
  background: var(--color-bg); border: 1px solid var(--color-border);
  min-width: 80px; min-height: 44px; transition: all var(--transition-fast);
}
.progress-step.active { background: var(--color-accent); color: #fff; border-color: var(--color-accent); }
.progress-step.completed { background: var(--color-success-bg); color: var(--color-success); border-color: var(--color-success); }
.step-num { font-weight: 600; font-size: 16px; }
```

### JS State Machine
```javascript
function goToStep(step) {
  if (step === 2 && !document.getElementById('selectedDoctorId').value) return;
  if (step === 3 && !document.getElementById('selectedDate').value) return;
  if (step === 4 && !document.getElementById('selectedStartTime').value) return;

  document.querySelectorAll('.booking-step').forEach(s => s.classList.remove('active'));
  document.getElementById('step' + step).classList.add('active');

  document.querySelectorAll('.progress-step').forEach(s => {
    const stepNum = parseInt(s.dataset.step);
    s.classList.remove('active', 'completed');
    if (stepNum === step) s.classList.add('active');
    else if (stepNum < step) s.classList.add('completed');
  });
  currentStep = step;

  if (step === 2) loadDates();
  if (step === 3) loadSlots();
  if (step === 4) updateSummary();
}
```

---

*Generated from session hardening + redesigning the Dizi Doc appointment app (PHP+CSV, Fedora/SELinux, Docker).*