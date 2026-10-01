#!/usr/bin/env bash
# curl + CSRF POST template — copy and adapt for any CSRF-protected form
# (PHP installers, admin logins, booking APIs that require a token).
#
# Usage:
#   ./curl-csrf.sh <BASE_URL> [--method POST] [--page <form path>] [field=value ...]
#
# Pattern that works reliably against session-bound CSRF tokens:
#   1. GET the page that RENDERS the form (capture the session cookie in the jar)
#   2. extract name="csrf_token" value="..." from that exact response
#   3. POST with the SAME jar; follow redirects (-L) and echo the final URL
set -euo pipefail

BASE="${1:?usage: $0 <BASE_URL> [field=value ...]}"
shift
JAR=$(mktemp)
FORM_HTML=$(mktemp)
RESP_HTML=$(mktemp)

# --- Adapt these per app ------------------------------------------------
FORM_URL="$BASE/install.php"   # page that renders the hidden csrf_token field
POST_URL="$BASE/install.php"   # URL the form submits to (often the same page)
# Fields as --data-urlencode "k=v" pairs (csrf_token is injected automatically):
FIELDS=()
# e.g. FIELDS=(--data-urlencode "email=admin@x.com" --data-urlencode "password=$PASS")
# -------------------------------------------------------------------------

curl -s -c "$JAR" "$FORM_URL" > "$FORM_HTML"
CSRF=$(grep -oE 'name="csrf_token" value="[^"]*"' "$FORM_HTML" | head -1 | sed 's/.*value="//;s/"//')
if [ -z "$CSRF" ]; then echo "ERROR: no csrf_token found in $FORM_URL" >&2; exit 1; fi

FINAL=$(curl -s -b "$JAR" -c "$JAR" -L -X POST "$POST_URL" \
  --data-urlencode "csrf_token=$CSRF" \
  "${FIELDS[@]}" \
  -o "$RESP_HTML" -w "%{url_effective}")

echo "final URL: $FINAL"
grep -E "Warning|Fatal|Invalid|error" "$RESP_HTML" | head -5 || true

rm -f "$JAR" "$FORM_HTML" "$RESP_HTML"