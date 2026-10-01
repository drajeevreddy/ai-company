# Docker-PHP verification & hardening — session detail (appointment app, 2026-08)

## Full-tree lint sweep (mandatory after pull/clone — targeted checks miss shipped bugs)
```bash
cd /home/painarise/appointment
while IFS= read -r f; do
  docker exec appointment php -l "/var/www/html/$f" 2>&1 | grep -q "No syntax errors" \
    || echo "BAD $f"
done < <(find . -name '*.php' -not -path './.git/*' | sed 's|^\./||' | sort)
```
Caught 2 admin pages (appointments.php, patients.php) that had 500'd SINCE THE
INITIAL COMMIT — the CSV-export block ended `exit;` without a `?>` close before
`<?php endif; ?>`. Signature: `PHP Parse error: syntax error, unexpected token
"<", expecting elseif/else/endif [line N]` at the `<?php endif; ?>` line.
Fix: insert a lone `?>` after `exit;`. Grep candidates: `exit;\n<?php`.
Lesson: lint sweep ALL files, not just the ones you edited.

## Verify-script hygiene (three self-inflicted failures in one session)
1. Asserted `>=3` CSRF hidden inputs on a manage-booking page — but the page only
   renders the VERIFY form (1 token) until a booking is verified; only then do the
   cancel + reschedule forms (2+ tokens) appear. Assert per page-state:
   `?booking_id=X&mobile=Y` renders the verified view; count tokens per state.
2. `set -u` script referenced `$VAR` before it was assigned → whole section "failed".
   Assign all vars before `set -u`, or pass them as args (`$1`, `$2`).
3. `docker exec php -l ...` without the container name → every file "BAD" for the
   same wrong reason. The container name is mandatory: `docker exec appointment php -l`.
4. CSRF extraction: hidden input `name="csrf_token" value="..."` vs `<meta
   name="csrf-token" content="...">` — grep the page's ACTUAL markup before
   writing the extraction regex.
Smoke-test ONE iteration of each check against the live page before trusting a
full run; if an entire section fails identically, suspect the script first.

## Hardened container (image appointment-php:hardened)
Dockerfile now bakes in: display_errors=Off, log_errors=On, expose_php=Off,
session cookie hardening (httponly, use_strict_mode, use_only_cookies,
samesite=Lax), ServerTokens Prod. Verified via curl -D -: no X-Powered-By, no
"Server: Apache/x.y". App-level error log: `@ini_set('error_log',
LOG_PATH . '/php-error.log')` in config.php (LOG_PATH defined earlier in file).

## Security additions shipped
- includes/LoginRateLimiter.php — per-IP JSON attempt file in data/ (5 fails →
  15-min lockout; cleared on success; prunes stale IPs). Wired into admin/login.php
  BEFORE CSRF check. NOTE: `data/login_attempts.json` needs an explicit .gitignore
  entry (`/data/login_attempts.json`) — `data/*.csv` ignores don't cover JSON.
- CSRF on public mutations: api/cancel.php + api/reschedule.php now reject
  token-less POSTs with 403; manage-booking.php forms carry tokens (verify form in
  unverified state; cancel/reschedule forms in verified state).
- Uploads: Helpers::isValidImageUpload() = extension + is_uploaded_file() +
  getimagesize() IMAGETYPE_JPEG/PNG/WEBP; uploads/.htaccess denies script
  extensions + dotfiles.
- Headers: Permissions-Policy, Referrer-Policy, X-Permitted-Cross-Domain-Policies,
  nosniff, SAMEORIGIN frame; dropped deprecated X-XSS-Protection; admin pages
  noindex, nofollow.

## Verification evidence (all passed)
Lockout: 5 wrong → "Too many failed attempts"; correct pw while locked → blocked;
rm attempts file → login → dashboard. API 403: cancel w/o token. CSRF form flow:
cancel → CSV status CANCELLED → rebook same slot → new booking id. Admin pages:
10/10 return 200 (incl. previously parse-broken). UI markers + enhanced CSS served.