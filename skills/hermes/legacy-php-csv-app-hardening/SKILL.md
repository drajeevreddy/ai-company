---
name: legacy-php-csv-app-hardening
category: devops
description: Harden PHP/CSV apps via Docker+Apache; security + mobile UX.
trigger: Harden PHP/CSV apps via Docker+Apache; security + mobile UX.
---

# Legacy PHP/CSV App Hardening & Deployment

## When to Use
- PHP app uses CSV files for data storage (no database)
- App security depends on `.htaccess` protecting `/data`, `/config`, `/includes`
- Need Docker deployment with Apache (PHP built-in server ignores `.htaccess`)
- Host runs SELinux Enforcing (Fedora/RHEL)
- Need to fix security gaps (CSRF, brute-force, header leaks, upload validation)
- Need mobile-first UX improvements for booking/forms

## Core Patterns

### 1. Docker + Apache Deployment (Mandatory)
```dockerfile
FROM php:8.3-apache
RUN a2enmod rewrite headers
# Add PHP hardening
RUN echo "display_errors=Off" >> $PHP_INI_DIR/conf.d/hardening.ini \
 && echo "expose_php=Off" >> $PHP_INI_DIR/conf.d/hardening.ini \
 && echo "session.use_strict_mode=1" >> $PHP_INI_DIR/conf.d/hardening.ini \
 && echo "session.cookie_httponly=1" >> $PHP_INI_DIR/conf.d/hardening.ini \
 && echo "session.cookie_secure=1" >> $PHP_INI_DIR/conf.d/hardening.ini \
 && echo "session.gc_maxlifetime=1440" >> $PHP_INI_DIR/conf.d/hardening.ini
```
- Run container: `docker run -d --name app --restart unless-stopped -p 8080:80 -v /host/path:/var/www/html:z php:8.3-apache`
- SELinux Enforcing requires `:z` bind mount flag
- No host PHP — lint via `docker exec app php -l /var/www/html/file.php`

### 2. File Ownership Model (Git + Container Writable)
```bash
# Tracked files owned by host user (UID 1000) for git
# Runtime dirs writable by both container (www-data) and host
chown -R 1000:1000 /host/path
chmod -R 777 /host/path/data /host/path/config /host/path/logs /host/path/uploads
```
- Replaces `chown www-data` model which blocked `git pull`
- 777 satisfies both container Apache writes and host git operations

### 3. Credential Management
- Admin password stored OUTSIDE repo: `/host/path/../app_admin_pass.txt`
- Never commit `data/*.csv` local changes: `git checkout -q -- data logs uploads` before pulls

### 4. Security Hardening Checklist
| Gap | Fix |
|-----|-----|
| No login brute-force | `LoginRateLimiter` class (5 fails/15min → lockout, JSON file in `/data`) |
| Session not hardened | `session.use_strict_mode=1`, `httponly`, `secure`, `gc_maxlifetime` in bootstrap.php |
| Errors leak to client | `ini_set('display_errors','0'); ini_set('log_errors','1'); error_log=/data/php-error.log` |
| CSRF missing on mutations | Add `Csrf::validateToken()` to all POST handlers + forms |
| Uploads executable | `uploads/.htaccess` deny `.php|.phtml|.phar|.pl|.py|.cgi|.sh` + `getimagesize()` validation |
| Header leaks | `expose_php=Off`, `ServerTokens Prod`, `Permissions-Policy`, `X-Frame-Options: SAMEORIGIN` |
| Admin indexed | `<meta name="robots" content="noindex, nofollow">` in admin header |

### 5. Common Bug Fixes
- **Parse error after `exit;` before `endif`**: Add `?>` before `<?php endif; ?>` in export blocks
- **`array_filter()` preserves keys**: Wrap result in `array_values()` in `CsvStorage::findAllWhere`
- **POST handlers after HTML output**: Move ALL `header('Location:')` logic BEFORE `require_once header.php`
- **Export CSV after HTML output**: Move export handlers BEFORE `header.php`
- **ZipArchive missing**: `apt-get install libzip-dev && docker-php-ext-install zip` in Dockerfile

### 6. Mobile UX Standards
| Element | Min Height | Notes |
|---------|------------|-------|
| Buttons (primary) | 52px (48px mobile) | `min-height`, `touchstart`/`touchend` opacity feedback |
| Progress steps | 44px (40px mobile) | |
| List items (doctor/date) | 80px (72-76px mobile) | |
| Date cards | 96px (84-88px mobile) | |
| Time slots | 64px (56-60px mobile) | |
| Form inputs | 16px font | Prevents iOS zoom on focus |
| Checkboxes | 20×20px | `accent-color: var(--primary)` |
| Responsive breakpoints | 768px / 480px | Stack grids, reduce padding |

### 7. Verification (No Test Suite)
Ad-hoc script pattern for PHP/CSV apps:
```bash
# 1. Lint all PHP: docker exec app php -l /var/www/html/file.php
# 2. Headers: curl -I → no X-Powered-By, no Server version, Permissions-Policy present
# 3. Protected paths: /data/ /config/ /includes/ /logs/ → 403
# 4. Brute force: 5 fails → lockout, correct pw blocked during lockout, reset after file delete
# 5. CSRF: API without token → 403, forms have tokens
# 6. Admin pages: all 200 after login, noindex present
# 7. UI elements: hero badge, stats, CTA band, chart canvas
# 8. Availability API: clean JSON, no PHP warnings
```

## Pitfalls
- **Don't use PHP built-in server** — ignores `.htaccess`, breaks security
- **Don't `chown www-data` on tracked files** — blocks `git pull`
- **Don't put export/POST handlers after `header.php`** — headers already sent
- **Don't forget `:z` on SELinux** — 403/500 on bind mount
- **Don't commit local CSV data** — use `git checkout -q -- data logs uploads`
- **Don't hardcode clinic names in code** — read from `config/settings.json` or `data/clinics.csv`

## Related Skills
- `hosting-php-apps` (for Hostinger-specific deployment)
- `website-security-hardening` (bundled, for general web hardening)

## References
- `references/docker-apache-selinux.md` — Docker + Apache + SELinux deployment recipe
- `references/csv-array-filter-bug.md` — `array_filter` key preservation fix
- `references/post-handler-ordering.md` — Moving handlers before HTML output
- `references/mobile-touch-targets.md` — Touch target sizing standards
- `scripts/verify-hardening.sh` — Ad-hoc verification script template