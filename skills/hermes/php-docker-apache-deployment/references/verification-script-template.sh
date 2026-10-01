#!/usr/bin/env bash
# Ad-hoc verification script TEMPLATE for PHP Docker apps with no test suite.
# COPY THIS FILE, FILL IN THE VARIABLES, RUN, THEN DELETE.
# NEVER COMMIT THIS SCRIPT.

set -euo pipefail

APP="/home/user/app"           # <-- absolute path to repo root
BASE="http://localhost:8080"   # <-- public URL
PASS="${1:-}"                  # <-- admin password (passed as arg or env)
CONTAINER="app"                # <-- docker container name

[[ -n "$PASS" ]] || { echo "Usage: $0 <admin_password>"; exit 1; }

fail=0

# --- 1. PHP lint (all files) ---
echo "== 1. php -l sweep =="
BAD=0
while IFS= read -r f; do
  docker exec "$CONTAINER" php -l "/var/www/html/$f" 2>&1 | grep -q "No syntax errors" \
    || { echo "FAIL lint: $f"; BAD=1; }
done < <(cd "$APP" && find . -name '*.php' -not -path './.git/*' | sed 's|^\./||' | sort)
[ "$BAD" = "0" ] && echo "OK all PHP files clean" || fail=1

# --- 2. Security headers / no version leaks ---
echo "== 2. headers =="
H=$(curl -s -D - -o /dev/null "$BASE/")
echo "$H" | grep -qiE "x-powered-by|Server: Apache/" && { echo "FAIL version leak"; fail=1; } || echo "OK no leaks"
for hdr in "X-Content-Type-Options: nosniff" "X-Frame-Options: SAMEORIGIN" "Referrer-Policy:" "Permissions-Policy:" "X-Permitted-Cross-Domain-Policies: none"; do
  echo "$H" | grep -qi "$hdr" && echo "OK $hdr" || { echo "FAIL missing $hdr"; fail=1; }
done

# --- 3. Protected paths return 403 ---
echo "== 3. protected paths =="
for p in data/ config/ includes/ logs/; do
  [ "$(curl -s -o /dev/null -w "%{http_code}" "$BASE/$p")" = "403" ] && echo "OK /$p 403" || { echo "FAIL /$p"; fail=1; }
done

# --- 4. Brute-force lockout (5/15min) + reset ---
echo "== 4. brute-force lockout =="
JAR=$(mktemp /tmp/hv_bf.XXXX); rm -f "$JAR"
CSRF=$(curl -s -c "$JAR" "$BASE/admin/login.php" | grep -oE 'name="csrf_token" value="[^"]*"' | sed 's/.*value="//;s/"//')
for i in 1 2 3 4 5; do
  curl -s -b "$JAR" -c "$JAR" -X POST "$BASE/admin/login.php" --data-urlencode "csrf_token=$CSRF" \
    --data-urlencode "email=admin@example.com" --data-urlencode "password=wrong$i" -o /dev/null
done
SIXTH=$(curl -s -b "$JAR" -c "$JAR" -X POST "$BASE/admin/login.php" --data-urlencode "csrf_token=$CSRF" \
  --data-urlencode "email=admin@example.com" --data-urlencode "password=wrong6")
echo "$SIXTH" | grep -qi "Too many failed attempts" && echo "OK lockout after 5" || { echo "FAIL lockout"; fail=1; }
# Correct password still blocked while locked
BLOCKED=$(curl -s -b "$JAR" -c "$JAR" -X POST "$BASE/admin/login.php" --data-urlencode "csrf_token=$CSRF" \
  --data-urlencode "email=admin@example.com" --data-urlencode "password=$PASS")
echo "$BLOCKED" | grep -qi "Too many" && echo "OK correct pw blocked during lockout" || { echo "FAIL sticky block"; fail=1; }
# Reset and verify login works
rm -f "$APP/data/login_attempts.json"
LOGIN=$(curl -s -b "$JAR" -c "$JAR" -L -X POST "$BASE/admin/login.php" --data-urlencode "csrf_token=$CSRF" \
  --data-urlencode "email=admin@example.com" --data-urlencode "password=$PASS" -o /dev/null -w "%{url_effective}")
echo "$LOGIN" | grep -q "dashboard" && echo "OK login after reset" || { echo "FAIL reset login"; fail=1; }

# --- 5. CSRF enforcement on mutation APIs ---
echo "== 5. CSRF gates =="
# Example: api/cancel.php without token -> 403
R=$(curl -s -X POST "$BASE/api/cancel.php" --data "booking_id=TEST&mobile=999" -w "|%{http_code}")
echo "$R" | grep -q '"success":false' && echo "$R" | grep -q '|403' && echo "OK cancel w/o token -> 403" || { echo "FAIL cancel CSRF: $R"; fail=1; }

# --- 6. Admin pages render (incl. any previously broken) ---
echo "== 6. admin pages =="
for p in appointments patients doctors schedules clinics holidays settings dashboard calendar analytics; do
  C=$(curl -s -b "$JAR" -L -o /dev/null -w "%{http_code}" "$BASE/admin/$p.php")
  [ "$C" = "200" ] && echo "OK $p.php" || { echo "FAIL $p.php -> $C"; fail=1; }
done

# --- 7. E2E booking flow ---
echo "== 7. E2E booking =="
B_JAR=$(mktemp /tmp/hv_bk.XXXX); rm -f "$B_JAR"
B_CSRF=$(curl -s -c "$B_JAR" "$BASE/book.php" | grep -oE 'name="csrf_token" value="[^"]*"' | sed 's/.*value="//;s/"//' | head -1)
BOOK=$(curl -s -b "$B_JAR" -X POST "$BASE/api/book.php" -H "Content-Type: application/json" \
  -d "{\"csrf_token\":\"$B_CSRF\",\"doctor_id\":\"DOC-XXX\",\"date\":\"2026-08-15\",\"start_time\":\"09:00\",\"end_time\":\"10:00\",\"name\":\"Test\",\"mobile\":\"999\",\"consent\":\"1\"}")
echo "$BOOK" | grep -q '"success":true' && echo "OK booked" || { echo "FAIL book: $BOOK"; fail=1; }
BID=$(echo "$BOOK" | grep -o '"booking_id":"[^"]*"' | sed 's/.*":"//;s/"//')
# Duplicate blocked
DUP=$(curl -s -b "$B_JAR" -X POST "$BASE/api/book.php" -H "Content-Type: application/json" \
  -d "{\"csrf_token\":\"$B_CSRF\",\"doctor_id\":\"DOC-XXX\",\"date\":\"2026-08-15\",\"start_time\":\"09:00\",\"end_time\":\"10:00\",\"name\":\"Test\",\"mobile\":\"999\",\"consent\":\"1\"}")
echo "$DUP" | grep -q '"success":false' && echo "$DUP" | grep -q '|400' && echo "OK duplicate blocked" || { echo "FAIL duplicate: $DUP"; fail=1; }
# Cancel
M_JAR=$(mktemp /tmp/hv_mg.XXXX); rm -f "$M_JAR"
MCSRF=$(curl -s -c "$M_JAR" "$BASE/manage-booking.php?booking_id=$BID&mobile=999" | grep -oE 'name="csrf_token" value="[^"]*"' | sed 's/.*value="//;s/"//' | head -1)
curl -s -b "$M_JAR" -L -X POST "$BASE/manage-booking.php" --data-urlencode "action=cancel" --data-urlencode "csrf_token=$MCSRF" --data-urlencode "booking_id=$BID" --data-urlencode "mobile=999" -o /dev/null
grep "$BID" "$APP/data/appointments.csv" | grep -q "CANCELLED" && echo "OK cancel -> CANCELLED" || { echo "FAIL cancel"; fail=1; }

# --- 8. Availability API clean JSON (no warnings) ---
echo "== 8. availability clean =="
AV=$(curl -s "$BASE/api/availability.php?doctor=DOC-XXX&date=2026-08-16")
echo "$AV" | grep -q '"success":true' && ! echo "$AV" | grep -qiE "Warning|Fatal" && echo "OK clean JSON" || { echo "FAIL availability"; fail=1; }

# Cleanup
rm -f "$JAR" "$B_JAR" "$M_JAR"

echo
[ "$fail" = "0" ] && echo "ALL CHECKS PASSED" || { echo "FAILURES PRESENT"; exit 1; }