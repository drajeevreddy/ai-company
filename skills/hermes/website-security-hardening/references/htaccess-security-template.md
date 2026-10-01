# .htaccess security template (Apache 2.4 / LiteSpeed shared hosting)

Validated with `httpd -t` against Apache 2.4.68. Place BEFORE the www→non-www and HTTPS rewrite rules; mod_alias RedirectMatch and mod_rewrite coexist fine.

## Root .htaccess security block

```apache
# Security headers
<IfModule mod_headers.c>
    Header always set X-Content-Type-Options "nosniff"
    Header always set X-Frame-Options "DENY"
    Header always set X-XSS-Protection "1; mode=block"
    Header always set Referrer-Policy "strict-origin-when-cross-origin"
    Header always set Permissions-Policy "geolocation=(), microphone=(), camera=()"
    Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
    Header always set Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' https://www.googletagmanager.com https://www.google-analytics.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; frame-src https://www.google.com https://maps.google.com; connect-src 'self' https://www.google-analytics.com https://www.googletagmanager.com; object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'self'"
    Header always set Access-Control-Allow-Origin "https://YOUR-DOMAIN.com"
    Header always unset X-Powered-By
</IfModule>

# Disable directory listing
Options -Indexes

# Block sensitive files (backups, configs, archives, source)
<FilesMatch "\.(sql|bak|old|swp|tmp|log|ini|conf|cfg|yml|yaml|sh|py|pyc|zip|tar|gz|rar|7z|md|json)$">
    Order allow,deny
    Deny from all
</FilesMatch>

# Block version control / hidden dirs (returns 404, not 403 — reveals less)
RedirectMatch 404 ^/(\.git|\.svn|\.env|\.idea|\.vscode|\.htaccess|\.htpasswd)(/|$)
```

Notes:
- `Header always unset Server` was deliberately OMITTED — it can 500 on LiteSpeed and is controlled by ServerTokens anyway.
- `Options -Indexes` may already exist in a subdir .htaccess; harmless to repeat at root.
- `.well-known/` is NOT caught by the RedirectMatch above (good — security.txt stays reachable).

## Per-directory (blog/, admin/, etc.)

Mirror the block but adjust:
- `X-Frame-Options "SAMEORIGIN"` instead of DENY if the dir is legitimately framed (e.g. admin panel that was already SAMEORIGIN — don't tighten what you can't verify).
- Tighter CSP if the dir loads no external scripts: `script-src 'self' 'unsafe-inline'` is enough for a self-contained admin.
- Add `ErrorDocument 404 /dir/index.php` if a CMS handles 404s (keep whatever the site already had).

## Crafting the CSP from a resource inventory (do this BEFORE writing CSP)

1. `grep -rhoE '(src|href)="https?://[^"]+"' *.html | sort -u` → every external host
2. Count inline `<script>`, `<style>`, `onload=` handlers — if any exist, you MUST keep `'unsafe-inline'` in script-src/style-src (a strict nonce CSP would require touching content — forbidden under no-content-change constraints)
3. Iframes: Google Maps embeds live at `https://www.google.com/maps/embed` → `frame-src https://www.google.com`
4. Analytics beacons → `connect-src` needs `https://www.google-analytics.com https://www.googletagmanager.com`
5. `object-src 'none'`, `base-uri 'self'`, `form-action 'self'` (verify no external form actions first: `grep -rhoE 'action="[^"]*"' *.html`)

## Extension blocking — what NOT to block

- NEVER block `.txt` / `.xml` — robots.txt and sitemap.xml are public by design.
- `.json` blocking is only safe after confirming no client-side `fetch()` of json URLs:
  `grep -rn "fetch(\|\.json'" blog/ contact-submissions/ --include="*.php" --include="*.js" | grep -v file_get_contents`
  (server-side `file_get_contents` is unaffected — the admin reads data JSON that way.)
- Keep `Order allow,deny / Deny from all` (2.2-style) for consistency when the codebase already uses it — it still works on 2.4/LiteSpeed.

## Line endings

Hostinger/LiteSpeed sites often have CRLF files. When patching `.htaccess`, preserve the existing line-ending style — mixed endings can confuse some modules. Verify after editing: `file .htaccess`.
