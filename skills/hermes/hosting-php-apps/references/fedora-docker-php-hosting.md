# Fedora + Docker PHP hosting — session recipe & error signatures

Real-session detail (hosting github.com/Leohunk007/appointment, a PHP 8 / CSV-store doctor-booking app, at /home/painarise/appointment, container `appointment`, port 8080).

## Environment facts
- Fedora, `getenforce` → Enforcing. No host PHP (`php -v` empty), sudo requires password, Docker daemon usable without sudo.

## The working container setup
```bash
# Dockerfile (image appointment-php)
FROM php:8.3-apache
RUN a2enmod rewrite headers

docker run -d --name appointment --restart unless-stopped -p 8080:80 \
  -v /home/painarise/appointment:/var/www/html:z appointment-php
```

## Failure signatures (each seen live)
| Symptom | Cause | Fix |
|---|---|---|
| 403 + Apache log `AH00529: pcfg_openfile: unable to check htaccess` | SELinux blocks container reading host bind-mount files | add `:z` to `-v` |
| 500 + `Invalid command 'RewriteEngine', perhaps misspelled or defined by a module not included` | mod_rewrite not enabled in stock image | `a2enmod rewrite headers` |
| POST / actions succeed but API body starts with `<br /> Warning: fopen(...): Permission denied` | app runs as `www-data` (uid 33); runtime files owned by local user after cp/git | `chmod -R 777` runtime dirs; re-chown with `docker exec <c> chown -R uid:gid` |
| Admin login stays on login.php, no error shown | (a) CSV write fail → headers already sent → redirect never fires; (b) stale CSRF | check body for warnings; check `logs/app.log` |
| `Undefined array key 0` + `Trying to access array offset on null` in `AvailabilityEngine.php:148`, `CsvStorage.php:187` | `array_filter()` preserves keys; non-first matches keep indexes `[1]`.. → `$rows[0]` undefined | `array_values(array_filter(...))` |

## The hidden-engine bug (class of bug)
CsvStorage `findAllWhere()` ran `array_filter($all, ...)` directly. Filtering row 1..N-1 of a list yields `[1 => row]` — no key 0. Then:
- `findWhere()` → `$results[0]` → null → "not found" even though the row exists.
- Direct indexing in callers → PHP notices that corrupt every JSON response.
- **Dedup silently disabled**: `checkDuplicate()` used `findWhere`, so a second booking for the same patient/slot succeeded → two bookings for one slot.
Lesson: any row-store layer in PHP that filters should `array_values()` before consumers index `[0]`. Verify reject-paths in E2E (duplicate/capacity), not just happy paths.

## Installation sync check after `git pull` of a new version
- fetch; `git log --on-line HEAD..origin/master`; stash-with-pull can break when container root chowned the tree — stop that by using `docker exec <c> chown -R <uid>:<gid> /var/www/html` before a `pull` (container root > no host sudo).
- After pull: re-grep for hardcoded base paths, re-run `php -l`, re-run E2E smoke. Data dirs are `.gitignore`'d → survive pulls.
- Local tweaks kept as a local commit (with `user.name`/`user.email` flags — host git has no global identity) so future `${origin}` pulls stay clean.

## The CSRF cookie/curl pattern (condensed)
```bash
curl -s -c jar.txt $BASE/login.php > form.html
CSRF=$(grep -oE 'name="csrf_token" value="[^"]*"' form.html | sed 's/.*value="//;s/"//')
curl -s -b jar.txt -c jar.txt -L -X POST $BASE/login.php \
  --data-urlencode "csrf_token=$CSRF" --data-urlencode "email=..." --data-urlencode "password=..." ...
# expect final url_effective to include /dashboard
```
Notes:
- The public booking form on the homepage may ALSO not render a token (book.php does). Grep the exact page that renders the record form.
- PHP built-in server ignores .htaccess — DON'T use `php -S` for apps relying on .htaccess protections.
- Log twice per design: `Logger::warning('Login failed: invalid password')` with no CSRF-set entry; use the app log to tell CSRF-fail vs password-fail.

---

## Session Learnings (added from this engagement)

### Dropdown Menus Near Viewport Bottom Get Cut Off
**Symptom**: Action dropdowns on last table rows open downward and are clipped by viewport edge.
**Cause**: CSS `position: absolute; top: 100%` on `.dropdown-menu` opens below trigger.
**Fix**:
- CSS: add `.dropdown-menu-bottom { top: auto; bottom: 100%; margin-bottom: 4px; }`
- JS (on click in `admin.js`): 
  ```js
  const rect = toggle.getBoundingClientRect();
  const menuHeight = menu.offsetHeight || 200;
  const spaceBelow = window.innerHeight - rect.bottom;
  if (spaceBelow < menuHeight + 10) {
      menu.classList.add('dropdown-menu-bottom');
  } else {
      menu.classList.remove('dropdown-menu-bottom');
  }
  ```
Verified on appointments.php (7 action dropdowns in last rows, all now flip upward when near bottom).

### Analytics Charts in Legacy PHP (No Build Step)
**Solution**: Drop-in Chart.js via CDN + inline data:
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<canvas id="monthlyChart" height="120"></canvas>
<script>
const months = <?= json_encode(array_keys($bookingsByMonth)) ?>;
const counts = <?= json_encode(array_values($bookingsByMonth)) ?>;
new Chart(ctx, { 
    type: 'bar', 
    data: { labels: months, datasets: [{ label: 'Appointments', data: counts, backgroundColor: '#3b82f6' }] },
    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } } }
});
</script>
```
No build step, works in any PHP admin page. Added to `analytics.php`.

### POST Handlers / Download Handlers Must Precede ALL HTML Output
**Two separate bugs, same root cause**:
1. `appointments.php` — POST action handlers (confirm/cancel/complete/noshow) ran after `require_once 'partials/header.php'` → `header('Location: ...')` silently failed (headers already sent)
2. `settings.php` — `?backup=1` zip download handler ran after `header.php` → `header('Content-Type: application/zip')` silently dropped, served HTML instead of zip

**Fix for both**: Move ALL POST handlers and GET export/backup handlers **before** any `require_once` that emits HTML. Keep role-gate before handler, then headers + exit.

### ZipArchive Missing in Container
**Symptom**: Backup download serves HTML instead of zip (after fixing handler position).
**Fix**: Add to Dockerfile:
```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends libzip-dev \
    && docker-php-ext-install zip \
    && rm -rf /var/lib/apt/lists/*
```

### Brand/Contact Data Has Multiple Sources — Update All Layers
**Pattern found during Dizi Doc rebrand**:
- Page title → `settings.json` `clinic_name` (index.php reads `$settings['clinic_name'] ?? APP_TITLE`)
- Admin login email → `users.csv` email column
- Contact display → `clinics.csv` clinic_name/phone/email
- WhatsApp links → `clinics.csv` whatsapp column
- ICS PRODID/UID → `CalendarService.php` (hardcoded)
- Backup filenames → `settings.php` (hardcoded)
- App name constant → `config/config.php` `APP_NAME`

**Fix**: Grep the variable assignment chain (`$clinicName = $settings['clinic_name'] ?? ...`) and update EVERY layer: `config/settings.json`, `data/clinics.csv`, `data/users.csv`, plus code constants (`APP_NAME`, ICS PRODID/UID, backup filenames). A rename in only one layer silently won't propagate.

### Display Masking Corrupts Data Edits
**Critical**: Terminal/file reads mask sensitive literals (phones, tokens) as `+918****8000`. Copy-pasting masked display writes literal asterisks to disk.
**Fix**: Write contact/credential data with `python3` (exact values) and verify byte-level via fingerprints (length, digit-count, no `*`), never by eye.

### Slot Granularity Change
**Requirement**: Hourly slots (9–10, 10–11, … 16–17) instead of single all-day 9–17 block.
**Implementation**: 
- Regenerate `data/schedules.csv` with 40 rows (Mon–Fri × 8 hours), each `slot_capacity=3`
- Availability engine naturally splits by `start_time`–`end_time` per schedule row
- Booking API unchanged — still takes exact `start_time`/`end_time`

### Flexible Admin Schedule UI
**Already present**: `schedules.php` has full per-slot CRUD (add/edit/delete any time window, copy day-to-day). Verified working with hourly slots.

---

## Verification Commands (ad-hoc)

```bash
# 1. Lint
docker exec appointment php -l /var/www/html/config/config.php
docker exec appointment php -l /var/www/html/includes/Auth.php
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

# 7. Dropdown flip (visual check)
# Open appointments.php, scroll to last rows, click Actions — menu opens UPWARD
```