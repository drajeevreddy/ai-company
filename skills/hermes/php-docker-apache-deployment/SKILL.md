---
name: php-docker-apache-deployment
description: Deploy PHP apps with Apache in Docker on SELinux Enforcing.
trigger: Use when deploying a PHP application that relies on .htaccess for security and must run on Fedora/RHEL with SELinux Enforcing.
---

# PHP + Docker + Apache Deployment Skill

## When to Use
- Legacy PHP apps using CSV/flat-file storage with `.htaccess` protecting sensitive directories
- Apps that break on PHP built-in server (`php -S`) because it ignores `.htaccess`
- Host: Fedora/RHEL with SELinux Enforcing
- Need to keep local fixes while staying current with upstream GitHub repo

## Core Principles

### 1. Apache in Docker, Not Built-in Server
**Why**: `.htaccess` rules (deny access to `/data`, `/config`, `/includes`) are security-critical. PHP's built-in server ignores them.
**How**: 
```dockerfile
FROM php:8.3-apache
RUN a2enmod rewrite headers
# + production hardening (see below)
```
Run: `docker run -d --name app --restart unless-stopped -p 8080:80 -v /host/path:/var/www/html:z image:tag`

### 2. SELinux `:z` Flag is Mandatory
On Fedora/RHEL with `getenforce = Enforcing`, bind mounts need `:z` relabel:
```bash
-v /home/user/app:/var/www/html:z
```
Without it: 403/500 errors from container Apache.

### 3. Ownership Model: `1000:1000` + `chmod 777` Runtime Dirs
**Problem**: Container Apache runs as `www-data` (UID 33); host user is `1000`. `chown www-data` blocks `git pull`.
**Solution**:
```bash
# Tracked files: owned by host (1000:1000) for git
docker exec app chown -R 1000:1000 /var/www/html
# Runtime dirs: writable by both container and host
chmod -R 777 data config logs uploads
```
This satisfies both Apache writes and host `git` operations.

### 4. Never Commit Credentials or Local Data
- Admin password lives **outside repo** (e.g., `/home/user/app_admin_pass.txt`)
- Seeded CSV data (`data/*.csv`) must not be pushed
- Use `git checkout -q -- data logs uploads` to discard local data churn before commit

### 5. Upstream Sync Workflow
```bash
# Local fixes committed locally (not stashed)
git add fixed-files.php
git commit -m "Local fix: description"

# Pull upstream
git fetch origin
git pull --ff-only origin master  # fails if local commits overlap; rebase instead

# Re-apply path fixes if upstream reintroduces hardcoded paths
grep -r "/old-path/" --include="*.php" .
# patch files again
git commit -am "Re-apply path fixes after upstream pull"
git push origin master
```

## Security Hardening Checklist (apply in this order)

| Layer | Action | File |
|-------|--------|------|
| Rate limiting | Per-IP login attempt limiter (5/15min lockout, JSON file in `data/`) | `includes/LoginRateLimiter.php` + wire into `admin/login.php` |
| Session | `session.use_strict_mode=1`, cookie-only, `session.gc_maxlifetime=1440` | `includes/bootstrap.php` |
| Errors | `display_errors=0`, `log_errors=1`, `error_log=data/php-error.log` | `config/config.php` |
| CSRF | Add to **all** mutation endpoints: `api/cancel.php`, `api/reschedule.php`, `manage-booking.php` forms | — |
| Uploads | `uploads/.htaccess` deny script execution; `getimagesize()` content validation | `uploads/.htaccess`, `includes/Helpers.php::isValidImageUpload()` |
| Headers | `X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN`, `Permissions-Policy`, `Referrer-Policy`, `X-Permitted-Cross-Domain-Policies: none` | `.htaccess` (mod_headers) |
| Admin | `<meta name="robots" content="noindex, nofollow">` on all admin pages | `admin/partials/header.php` |
| Docker PHP | `display_errors=Off`, `expose_php=Off`, `ServerTokens Prod` | `Dockerfile` + `conf.d/hardening.ini` |

## Common Bug Patterns & Fixes

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

### ZipArchive Missing in Container
**Symptom**: Backup download serves HTML instead of zip.
**Fix**: Add to Dockerfile:
```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends libzip-dev \
    && docker-php-ext-install zip \
    && rm -rf /var/lib/apt/lists/*
```

## Verification (No Test Suite? Ad-hoc Script Pattern)
Since legacy PHP apps often lack PHPUnit/lint CI:
1. Write a **throwaway bash script** under `/tmp/verify-*.sh`
2. Run checks: lint (`docker exec php -l`), headers, protected paths, auth flows, CSRF gates, E2E booking
3. Delete script after green run
4. Never commit verification scripts

Example checks:
- `php -l` on all PHP files via container
- `curl -I` for security headers, no version leaks
- Protected dirs return 403
- Brute-force lockout triggers and resets
- CSRF-less API calls return 403
- Booking create → duplicate blocked → cancel → rebook works

## Rebranding Pattern (if needed)
1. Find all brand strings: `grep -r "OldBrand" --include="*.php" .`
2. Centralize in `config/config.php`: `define('APP_NAME', 'NewBrand');`
3. Update: titles, logos, install pages, ICS PRODID/UID, backup filenames
4. Update data layer: `clinics.csv` clinic_name, `settings.json` clinic_name, `users.csv` admin email
5. Verify: homepage title, admin login, ICS output, backup download header

## References
- `references/selinux-bind-mount.md` — SELinux `:z` flag details
- `references/ownership-model.md` — Why 1000:1000 + 777 works
- `references/verification-script-template.sh` — Reusable ad-hoc verification skeleton
- `references/security-hardening-checklist.md` — Full checklist with file locations