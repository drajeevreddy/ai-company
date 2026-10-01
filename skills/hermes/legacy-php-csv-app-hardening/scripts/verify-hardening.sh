#!/usr/bin/env bash
# Ad-hoc verification script for legacy PHP/CSV app hardening
# Usage: bash verify-hardening.sh <admin_password>
# Run from app root directory

set -euo pipefail

APP_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BASE="http://localhost:8080"
PASS="${1:-}"
fail=0

if [[ -z "$PASS" ]]; then
    echo "Usage: $0 <admin_password>"
    exit 1
fi

echo "=== 1. PHP Lint ==="
while IFS= read -r f; do
    if ! docker exec appointment php -l "/var/www/html/$f" 2>&1 | grep -q "No syntax errors"; then
        echo "FAIL lint: $f"
        fail=1
    fi
done < <(cd "$APP_ROOT" && find . -name '*.php' -not -path './.git/*' | sed 's|^\./||' | sort)
[[ $fail -eq 0 ]] && echo "OK all PHP files clean"

echo "=== 2. Security Headers ==="
H=$(curl -s -D - -o /dev/null "$BASE/")
echo "$H" | grep -qiE "x-powered-by|Server: Apache/" && { echo "FAIL version leak"; fail=1; } || echo "OK no version leaks"
for hdr in "X-Content-Type-Options: nosniff" "X-Frame-Options: SAMEORIGIN" "Referrer-Policy:" "Permissions-Policy:" "X-Permitted-Cross-Domain-Policies: none"; do
    echo "$H" | grep -qi "$hdr" && echo "OK $hdr" || { echo "FAIL missing $hdr"; fail=1; }
done

echo "=== 3. Protected Paths (403) ==="
for p in data/ config/ includes/ logs/; do
    [[ "$(curl -s -o /dev/null -w "%{http_code}" "$BASE/$p")" = "403" ]] && echo "OK /$p -> 403" || { echo "FAIL /$p"; fail=1; }
done

echo "=== 4. Brute-Force Lockout ==="
JAR=$(mktemp /tmp/hv_jar.XXXX); rm -f "$JAR"
CSRF=$(curl -s -c "$JAR" "$BASE/admin/login.php" | grep -oE 'name="csrf_token" value="[^"]*"' | sed 's/.*value="//;s/"//')
for i in 1 2 3 4 5; do
    curl -s -b "$JAR" -c "$JAR" -X POST "$BASE/admin/login.php" \
        --data-urlencode "csrf_token=$CSRF" \
        --data-urlencode "email=owner@example.com" --data-urlencode "password=x$i" -o /dev/null
done
SIX=$(curl -s -b "$JAR" -c "$JAR" -X POST "$BASE/admin/login.php" \
    --data-urlencode "csrf_token=$CSRF" \
    --data-urlencode "email=owner@example.com" --data-urlencode "password=x6")
echo "$SIX" | grep -qi "Too many failed attempts" && echo "OK lockout after 5 fails" || { echo "FAIL lockout"; fail=1; }
rm -f "$APP_ROOT/data/login_attempts.json"
OK=$(curl -s -b "$JAR" -c "$JAR" -L -X POST "$BASE/admin/login.php" \
    --data-urlencode "csrf_token=$CSRF" \
    --data-urlencode "email=owner@example.com" --data-urlencode "password=$PASS" -o /dev/null -w "%{url_effective}")
echo "$OK" | grep -q "dashboard" && echo "OK login resumes after reset" || { echo "FAIL reset login"; fail=1; }

echo "=== 5. CSRF Enforcement ==="
R=$(curl -s -X POST "$BASE/api/cancel.php" --data "booking_id=SHA-260811-001&mobile=9876001122" -w "|%{http_code}")
echo "$R" | grep -q '"success":false' && echo "$R" | grep -q '|403' && echo "OK api/cancel w/o token -> 403" || { echo "FAIL CSRF: $R"; fail=1; }

echo "=== 6. Admin Pages (200 + noindex) ==="
for p in appointments.php patients.php doctors.php schedules.php clinics.php holidays.php settings.php dashboard.php calendar.php analytics.php; do
    C=$(curl -s -b "$JAR" -L -o /dev/null -w "%{http_code}" "$BASE/admin/$p")
    [[ "$C" = "200" ]] && echo "OK $p" || { echo "FAIL $p -> $C"; fail=1; }
done
curl -s -b "$JAR" "$BASE/admin/appointments.php" | grep -qi "noindex" && echo "OK admin noindex" || { echo "FAIL noindex"; fail=1; }

echo "=== 7. Exports (CSV) ==="
for p in "appointments.php?export=1" "patients.php?export=1"; do
    r=$(curl -s -b "$JAR" -w "%{http_code} %{content_type}" -o /dev/null "$BASE/admin/$p")
    echo "$r" | grep -q "200 text/csv" && echo "OK $p" || { echo "FAIL $p: $r"; fail=1; }
done

echo "=== 8. Settings Backup Zip ==="
BK=$(curl -s -b "$JAR" -D /tmp/hv_bk.h -o /tmp/hv_bk.zip -w "%{http_code}" "$BASE/admin/settings.php?backup=1")
grep -qi 'Content-Disposition.*dizi-doc-backup-' /tmp/hv_bk.h && file -b /tmp/hv_bk.zip | grep -q '^Zip archive' \
    && echo "OK backup zip" || { echo "FAIL backup"; fail=1; }
rm -f /tmp/hv_bk.h /tmp/hv_bk.zip

echo "=== 9. Mobile UX Elements ==="
UI=$(curl -s "$BASE/")
echo "$UI" | grep -q 'class="hero-badge"' && echo "OK hero badge" || { echo "FAIL hero badge"; fail=1; }
echo "$UI" | grep -q 'class="hero-stats"' && echo "OK hero stats" || { echo "FAIL hero stats"; fail=1; }
echo "$UI" | grep -q 'class="cta-band"' && echo "OK CTA band" || { echo "FAIL CTA band"; fail=1; }
CSS=$(curl -s "$BASE/assets/css/app.css")
for term in "min-height: 52px" "min-height: 44px" "font-size: 16px" "width: 20px" "accent-color" "@media (max-width: 768px)" "@media (max-width: 480px)"; do
    echo "$CSS" | grep -q "$term" && echo "OK CSS: $term" || { echo "MISSING CSS: $term"; fail=1; }
done
JS=$(curl -s "$BASE/assets/js/booking.js")
echo "$JS" | grep -q "touchstart" && echo "OK touchstart" || { echo "MISSING touchstart"; fail=1; }
echo "$JS" | grep -q "touchend" && echo "OK touchend" || { echo "MISSING touchend"; fail=1; }

echo "=== 10. Availability API Clean JSON ==="
AV=$(curl -s "$BASE/api/availability.php?doctor=DOC-BE6FDE5A&date=2026-08-12")
echo "$AV" | head -c 60 | grep -q '"success":true' && echo "OK clean JSON" || { echo "FAIL availability: $(echo "$AV" | head -c 120)"; fail=1; }
echo "$AV" | grep -qiE "Warning|Fatal" && { echo "FAIL warning leaked"; fail=1; } || echo "OK no PHP warnings in body"

rm -f "$JAR"
echo
[[ $fail -eq 0 ]] && echo "ALL CHECKS PASSED" || { echo "FAILURES PRESENT"; exit 1; }