---
name: hosting-php-apps
description: "Use when hosting PHP web apps (Docker, Hostinger)."
---

# Hosting PHP Web Apps

Take a PHP app (often a fresh GitHub clone) to a WORKING hosted URL — locally in Docker (this box's reliable path) or on user's Hostinger hPanel — then prove it works end-to-end with curl and real file checks.

## When to use
- "pull this and host for me", "host this PHP app", "deploy this site"
- Installing via an app's PHP installer (install.php) headlessly
- Verifying a fresh hosting end-to-end (homepage, APIs, admin login, a real mutation)

## Host constraints on this box
- Fedora, SELinux **Enforcing**, NO host PHP, no passwordless sudo.
- Docker works without sudo; use `php:8.x-apache` images (e.g. php:8.3-apache).
- Production hosting for user sites = Hostinger hPanel (File Manager/FTP, no stored creds — tell user what to upload).
- **Do NOT leave the app in /tmp** — systemd-tmpfiles cleans /tmp after ~10 days. Move to /home/painarise/<app>.

## Local Docker workflow
1. Clone → read README.md + config/ + .htaccess FIRST (rewrite rules, protected dirs, runtime-dir permission needs).
2. Build a custom image — stock php:8.x-apache lacks rewrite: `FROM php:8.3-apache` + `RUN a2enmod rewrite headers` (else 500 "Invalid command 'RewriteEngine'").
3. Run: `docker run -d --name <app> --restart unless-stopped -p 8080:80 -v /home/painarise/<app>:/var/www/html:z <image>`
   - VOLUME FLAG **`:z` is mandatory on SELinux hosts** — without it: 403 `pcfg_openfile: ... unable to check htaccess`.
4. Make runtime dirs (data/config/logs/uploads) writable by container's www-data (uid 33): `chmod -R 777` those dirs. (App writes CSV/JSON/log files at runtime.)
5. Run installer headlessly: GET form with cookie jar → extract `name="csrf_token" value="..."` → POST with same jar (see scripts/curl-csrf-post.sh).
6. E2E verify EVERYTHING: homepage 200; APIs return **clean JSON (no PHP Warning/Fatal lines)**; admin login (CSRF+cookies, follow redirect → dashboard); create a record via the public flow; check the CSV/JSON store as ground truth; test a reject path (duplicate/capacity) too. Save admin creds OUTSIDE the web root and tell the user the path.
7. Seed with the user's real business details (clinic name, phone, WhatsApp) — they can change later.

## Pitfalls (each one burned this class of task)
- **PHP warnings leak into HTTP bodies** → API JSON is corrupted. Always `grep -E 'Warning|Fatal'` every response during verification.
- `array_filter()` **keeps keys**: filtered rows keep original indices, so `$rows[0]` fails mid-list with "Undefined array key 0" → notices corrupt responses AND `findWhere`-style lookups silently return null → **duplicate checks silently bypassed** (double bookings!). Fix: wrap with `array_values(...)`.
- **cp -a / git operations change ownership** of www-data-created files → app can't write CSVs, login "fails" (302 back to login, warnings in body). Fix: `docker exec <app> chown -R uid:uid` (container runs as root — no sudo needed) then re-chmod runtime dirs.
- **Hardcoded base paths in third-party apps** (e.g. `Location: /doctor-booking/admin/login.php`): grep before hosting at root; fix to relative/root paths.
- install.php idiom `file_exists(...) && $json['installed'] ?? false` is an operator-precedence bug — capture the var first.
- Container recreate **destroys PHP sessions** — old cookie jars are invalid; refetch.
- CSRF is session-bound: stale token = login silently fails on the login page (nothing logged) vs wrong password (log "invalid password"). Check app log + rendered error to distinguish.
- `.gitignore`'d runtime files survive `git pull`; ownership/mode drift shows as `M data/.gitkeep` noise — reset with `git checkout -- <paths>`.
- **Display masking corrupts data edits**: file reads/terminal render sensitive literals (phones, tokens) MASKED (e.g. `+918****8000`). Copy-pasting a masked display value into a patch writes literal asterisks to disk (the old clinics.csv phone got scrubbed this way). Write contact/credential data with `python3` (exact values) and verify byte-level via fingerprints (length, digit-count, no `*`), not by eye.
- **Download/attach handlers must precede ALL HTML output**: a `?export`/`?backup` block placed after the HTML-emitting header partial has its `header()` calls SILENTLY DROPPED (headers already sent) — user downloads the page HTML instead of the file. Keep the handler immediately after auth gating, before any output; role-gate it before sending. Also, stock `php:8.3-apache` LACKS the `zip` ext — ZipArchive features fail silently; add `libzip-dev` + `docker-php-ext-install zip` to the image.
- **Brand/contact text has MANY sources**: page title often comes from `settings.json` (clinic_name), admin login email from `users.csv`, contact display from `clinics.csv`. Before renaming/updating contacts, grep the variable's assignment (e.g. index.php `$clinicName = $settings['clinic_name'] ?? APP_TITLE`) and update EVERY layer — the rename silently won't propagate otherwise.

## Verification
- Lint: `docker exec <app> php -l /var/www/html/<file>` (no host PHP).
- Regression proof: hit the exact prior-failure endpoint(s), confirm clean JSON/200.

## Support files
- `references/fedora-docker-php-hosting.md` — full session recipe + error signatures/troubleshooting (SELinux, a2enmod, ownership trap, CsvStorage fix).
- `references/rebrand-contact-data-layers.md` — the Dizi Doc rebrand pass: where each brand/contact string lives, display-masking corruption, the zip-download headers fix.
- `scripts/curl-csrf-post.sh` — copy-and-adapt curl template for any CSRF-protected POST (installs, logins, APIs).