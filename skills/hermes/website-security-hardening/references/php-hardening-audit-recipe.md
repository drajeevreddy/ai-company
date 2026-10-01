# PHP web-app hardening audit — verified recipe (booking app, 2026-08)

Applied + fully verified (ad-hoc scripts, all green) on a php:8.3-apache Docker app
(CSV-store doctor-booking). Checks apply equally to shared hosting via .htaccess.

## 1. CSRF on public mutation APIs (the usual gap)
Admin forms usually have CSRF; public `api/*.php` endpoints often don't.
- Grep all api endpoints for validation: `grep -ln "csrf" api/*.php` — any mutating
  endpoint (cancel / reschedule / delete / status-change) must call
  `Csrf::validateToken($_POST['csrf_token'] ?? $data['csrf_token'])` BEFORE mutating.
- Proof: token-less POST → expect HTTP 403 (use `-w '|%{http_code}'`).

## 2. Upload real-content validation (extension check is insufficient)
A `.php` renamed to `.jpg` passes extension whitelists. Add:
```php
public static function isValidImageUpload(array $file): bool
{
    if (empty($file['tmp_name']) || !is_uploaded_file($file['tmp_name'])) return false;
    if (!self::isValidImage($file['name'] ?? '')) return false;          // extension gate
    if ((int)($file['size'] ?? 0) > 5 * 1024 * 1024) return false;
    $info = @getimagesize($file['tmp_name']);                            // content sniff
    return $info !== false && in_array($info[2], [IMAGETYPE_JPEG, IMAGETYPE_PNG, IMAGETYPE_WEBP], true);
}
```
Plus `uploads/.htaccess` (defense-in-depth even if a script name slips through):
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

## 3. Info-leak suppression (prove with curl)
Docker image layer (runs before app):
```
RUN echo "display_errors=Off" >> $PHP_INI_DIR/conf.d/hardening.ini \
 && echo "log_errors=On" >> $PHP_INI_DIR/conf.d/hardening.ini \
 && echo "expose_php=Off" >> $PHP_INI_DIR/conf.d/hardening.ini \
 && echo "session.cookie_httponly=1" >> $PHP_INI_DIR/conf.d/hardening.ini \
 && echo "session.use_strict_mode=1" >> $PHP_INI_DIR/conf.d/hardening.ini \
 && echo "session.use_only_cookies=1" >> $PHP_INI_DIR/conf.d/hardening.ini \
 && echo "session.cookie_samesite=Lax" >> $PHP_INI_DIR/conf.d/hardening.ini \
 && sed -i 's/^ServerTokens OS/ServerTokens Prod/' /etc/apache2/conf-enabled/security.conf
```
App-level (config.php, after defines so LOG_PATH exists):
```php
ini_set('display_errors', '0');
ini_set('log_errors', '1');
@ini_set('error_log', LOG_PATH . '/php-error.log');
```
Verify: `curl -sD - -o /dev/null http://host/` — must show NO `X-Powered-By`,
no `Server: Apache/x.y`, and every security header present.

## 4. .htaccess headers (root)
```
Header set X-Content-Type-Options "nosniff"
Header set X-Frame-Options "SAMEORIGIN"
Header set Referrer-Policy "strict-origin-when-cross-origin"
Header set Permissions-Policy "camera=(), microphone=(), geolocation=(), interest-cohort=()"
Header set X-Permitted-Cross-Domain-Policies "none"
```
(drop obsolete `X-XSS-Protection; browsers ignore it.) Admin pages: noindex meta in the shared header partial.

## 5. Whole-tree lint sweep — catches pages broken since the FIRST commit
```bash
cd repo && while read f; do docker exec <container> php -l "/var/www/html/$f" \
  | grep -q 'No syntax errors' || echo "BAD $f"; done \
  < <(find . -name '*.php' -not -path './.git/*' | sed 's|^\./||' )
```
Signature to recognize: `PHP Parse error: syntax error, unexpected token "<",
expecting elseif/else/endif [line N]` → an `exit;`-style statement inside a
`<?php ... ?>` template block was NOT followed by `?>` before the next
`<?php endif; ?>` — the parser stays in PHP mode and sees `<` as code. Pages 500
since the initial release; only a full tree sweep surfaces them (per-file diffs
won't). Fix: insert a lone `?>` after `exit;` before `<?php endif; ?>`.

## 6. Brute-force lockout functional test (already in login-rate-limiting.md)
5 wrong POSTs → lockout message; correct password while locked → still blocked;
delete the attempts JSON → correct login works again and clears the file.