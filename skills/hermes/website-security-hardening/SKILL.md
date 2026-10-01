---
name: website-security-hardening
description: "Fix website security issues without changing content."
---

# Website Security Hardening

Audit a website for security weaknesses, implement fixes at the server/config/PHP layer, and VERIFY them — especially when the user forbids changing visible content ("dont change any content", "fix these issues"). Applies to static HTML + PHP sites on shared Apache/LiteSpeed hosting (Hostinger/hpanel/hcdn etc.) where only `.htaccess` and PHP files are editable.

## Workflow

### 1. Recon (headers + surface) — never skip
- `curl -sI https://site/` — inventory current headers; note which are missing: HSTS, CSP (a lone `upgrade-insecure-requests` is weak), X-XSS-Protection, Referrer-Policy, Permissions-Policy.
- Probe sensitive paths: `/.env`, `/.git/config`, `/wp-admin`, `/phpmyadmin`, `/blog/admin`, `robots.txt`, `sitemap.xml`. Record what is ALREADY blocked at the CDN/hosting layer (then no code change is needed — keep that status).
- Inventory EXTERNAL RESOURCES before crafting a CSP: `grep -rhoE '(src|href)="[^"]*(http|cdn)[^"]*"' *.html` plus counts of inline `<script>`, `<style>`, and `onload=` handlers. Every host found must be allowed in the CSP or you break the site.
- Map existing protections so you don't regress them: nested data-dir `.htaccess` (`Order deny,allow` / `Deny from all`), CSRF tokens, `requireAuth()` gates, robots.txt blocks.

### 2. Server layer (.htaccess) — zero visible content changes
Add the security-header block, `Options -Indexes`, sensitive-file blocking, and dot-dir 404s to the root `.htaccess`; mirror (tighter CSP) in per-directory files like `blog/.htaccess`. Template + CSP-crafting method in `references/htaccess-security-template.md`.

### 3. PHP layer
- Admin login brute-force protection: JSON attempt log per IP in an already-protected data dir — 5 failures → 15-min lockout, expiry cleanup, cleared on success. Working code in `references/login-rate-limiting.md`.
- Session hardening in config BEFORE `session_start()`: `ini_set('session.cookie_httponly'...)`, `use_strict_mode`, `use_only_cookies`, `cookie_secure`, `cookie_samesite=Lax`, `gc_maxlifetime`.
- `session_regenerate_id(true)` inside `authenticate()` on success (session fixation).
- `noindex, nofollow` meta on every admin page; remove public footer links pointing at `/admin` AND the preceding `<span class="sep">|</span>` (else a dangling pipe renders).

### 4. Extras
- `security.txt` at `/.well-known/security.txt` — but check your dotfile blocking rules don't hide it.

### 5. VERIFY — mandatory (scripts are re-runnable)
- `scripts/verify-php-lint.sh <project> [dirs...]` — real `php -l` on every PHP file; auto-downloads a static PHP CLI if `php` isn't installed (no sudo needed).
- `scripts/verify-htaccess.sh <project> [rel .htaccess paths...]` — validates via real `httpd -t` by wrapping each file in a `<Directory>` block.
- Functional test: copy the real login.php into a scratch docroot with stubbed config/auth, boot `php -S`, then curl the brute-force scenario: 5 wrong POSTs → lockout message; correct password while locked → still blocked; back-date the attempts file (epoch < now-900) → login succeeds (302); success → attempts file is `[]`.
- Content integrity: diff live HTML against an untouched backup copy to PROVE only intended lines changed.

## Pitfalls (all hit in real sessions)
- **phply (pip) is a PHP5-era parser** — it cannot parse PHP7 `??`. Its "invalid syntax" failures on modern code are tool noise, not bugs. Use a real PHP binary for linting.
- **No sudo for dnf/apt?** Download a static PHP CLI: `https://dl.static-php.dev/static-php-cli/bulk/php-8.3.14-cli-linux-x86_64.tar.gz` → `tar -xzf` → `./php -l file.php`.
- **`httpd -t` does NOT parse `.htaccess` files** (they're read per-request). To validate: wrap each file's body in `<Directory "…">…</Directory>` inside a minimal config that `Include conf.modules.d/*.conf`, then `httpd -t -f`. Use `#` comments, not bare `===` lines, in generated configs.
- **CLI-vs-web SAPI trap**: `$_SERVER['HTTP_HOST']` is undefined in CLI; the warning prints to stdout, PHP treats that as "output", and session `ini_set` fails with "headers already sent". Not a real bug. Verify session settings through the web server (`php -S` + curl) or run `php -d display_errors=stderr`.
- `Header always unset Server` can 500 on LiteSpeed/Apache and is controlled by ServerTokens anyway — drop it (server-leak is LOW risk).
- CSP needs `'unsafe-inline'` for script+style when the site has inline gtag config, `onload="this.media='all'"` preload handlers, or inline styles. Don't attempt strict-nonce CSP on an unmodified static site.
- A CDN-injected CSP header (e.g. `upgrade-insecure-requests`) COMBINES with your origin CSP — browsers enforce the intersection; keep them compatible.
- When blocking extensions, never block `.txt`/`.xml` (robots.txt, sitemap.xml are public). Blocking `.json` is only safe after grepping for client-side `fetch()` of json URLs (admin code usually reads via `file_get_contents` server-side — safe).
- Multi-line edits with `sed`/`patch` on CRLF files: verify line endings and re-read the result; a stray BOM or separator removal is easy to miss.

## PHP CSV App Hardening Pattern (from Dizi Doc appointment app)
When hardening a PHP+CSV appointment/booking app on Fedora/SELinux:

**Container runtime (Fedora Enforcing)**
- Use `php:8.3-apache` base + custom image with `RUN a2enmod rewrite headers`
- Mount with `:z` relabel: `-v /path/to/app:/var/www/html:z`
- Hardened `php.ini` via `RUN echo "display_errors=Off\nexpose_php=Off\nerror_log=/var/log/php-error.log\n..." >> $PHP_INI_DIR/conf.d/hardening.ini`
- `ServerTokens Prod` + `ServerSignature Off` in Apache config

**Ownership model (git + Apache write coexistence)**
- Tracked files owned by host UID 1000 (`painarise`) → git works
- Runtime dirs `data/ config/ logs/ uploads/` chmod 777 → Apache (`www-data`) can write CSV
- Admin password kept OUTSIDE repo at `/home/user/app_admin_pass.txt` (survives /tmp wipe)

**Login hardening**
- `LoginRateLimiter` class: 5 failed attempts/IP/15min → lockout; JSON file in protected `data/` dir
- `session_regenerate_id(true)` on success; strict session cookies (httponly, secure, samesite=Lax, gc_maxlifetime)
- Admin pages: `noindex, nofollow` meta + auth gate in `partials/auth.php`

**CSRF coverage**
- All admin POST forms + mutation APIs (`api/cancel.php`, `api/reschedule.php`, `manage-booking.php`)
- `Csrf::generateToken()` in session, validated before any mutation

**Upload defense**
- `uploads/.htaccess` denies script execution (`.php`, `.pl`, etc.)
- `Helpers::isValidImageUpload()` uses `getimagesize()` + extension whitelist + random filenames

**Header hardening (root .htaccess)**
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: SAMEORIGIN`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=(), usb=(), interest-cohort=()`
- `X-Permitted-Cross-Domain-Policies: none`
- Remove `X-Powered-By` (expose_php=Off)

**Verification pattern (ad-hoc scripts for PHP/CSV apps without test suite)**
- `php -l` sweep on all PHP files via `docker exec <container> php -l /var/www/html/file.php`
- Security header presence + no version leaks (`curl -sI ... | grep -iE "x-powered-by|Server: Apache"`)
- Protected paths (`/data/`, `/config/`, `/includes/`, `/logs/`) → 403
- Brute-force lockout functional test (5 wrong → lockout; correct pw during lockout → blocked; clear attempts file → login works)
- CSRF enforcement: APIs without token → 403; forms carry token
- Admin pages all 200 after login (including previously parse-broken ones)
- Availability/booking APIs return clean JSON (no PHP warnings in body)
- Mobile touch targets in CSS (`min-height: 44px+`, `font-size: 16px` for iOS no-zoom)

**Common bugs found/fixed**
- Missing `?>` before `<?php endif; ?>` in admin export blocks (caused PHP 500)
- POST handlers running after HTML output → `header('Location:')` fails (move handlers before `header.php`)
- Backup zip download broken: headers sent before zip handler (move zip handler before any output, before `header.php`)
- Missing ZipArchive extension (add `docker-php-ext-install zip` to Dockerfile)
- CSV `array_filter()` preserves keys → `$results[0]` misses non-first-row matches (wrap in `array_values()`)

## Support files

## Support files
- `references/htaccess-security-template.md` — copy-paste root + per-dir .htaccess blocks, CSP crafting from a resource inventory, ordering notes.
- `references/login-rate-limiting.md` — brute-force PHP code, session-hardening ini_set block, session_regenerate_id, noindex, functional verification recipe.
- `scripts/verify-php-lint.sh` — php -l sweep with static-binary fallback.
- `scripts/verify-htaccess.sh` — httpd -t validation via Directory wrapping.
