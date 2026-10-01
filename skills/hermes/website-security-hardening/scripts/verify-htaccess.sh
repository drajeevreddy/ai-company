#!/usr/bin/env bash
# Validate .htaccess files with the REAL Apache binary.
#
# httpd -t does NOT parse .htaccess files at config-test time (they are read
# per-request). Workaround: wrap each .htaccess body inside a <Directory>
# block — the exact context Apache applies it in — within a minimal config,
# then `httpd -t` validates every directive against the installed modules.
#
# Usage:
#   verify-htaccess.sh <project-dir> [rel/path/.htaccess ...]
#   (defaults: .htaccess blog/.htaccess contact-submissions/.htaccess
#              blog/data/.htaccess contact-submissions/data/.htaccess)
#
# Exit 0 if all pass, 1 otherwise. Requires `httpd` on PATH (Fedora/RHEL:
# dnf install httpd).
set -u

PROJ="${1:?usage: verify-htaccess.sh <project-dir> [rel paths...]}"
shift
HTS=("$@")
[ ${#HTS[@]} -eq 0 ] && HTS=(
  .htaccess
  blog/.htaccess
  contact-submissions/.htaccess
  blog/data/.htaccess
  contact-submissions/data/.htaccess
)

command -v httpd >/dev/null || { echo "httpd not found — install httpd first" >&2; exit 2; }

TMPD="$(mktemp -d /tmp/hermes-verify-htaccess.XXXXXX)"
trap 'rm -rf "$TMPD"' EXIT

{
  echo 'ServerRoot "/etc/httpd"'
  echo "PidFile $TMPD/httpd.pid"
  echo 'Listen 127.0.0.1:8099'
  echo 'User apache'
  echo 'Group apache'
  echo "ErrorLog $TMPD/error.log"
  echo 'LogLevel emerg'
  echo 'Include conf.modules.d/*.conf'
  echo "DocumentRoot \"$PROJ\""
  echo "<Directory \"$PROJ\">"
  echo '    Options Indexes FollowSymLinks'
  echo '    AllowOverride All'
  echo '    Require all granted'
  echo '</Directory>'
  for ht in "${HTS[@]}"; do
    p="$PROJ/$ht"
    if [ ! -f "$p" ]; then
      echo "MISSING: $p (skipping)" >&2
      continue
    fi
    echo "# === $ht ==="
    echo "<Directory \"$(dirname "$p")\">"
    cat "$p"
    echo '</Directory>'
  done
} > "$TMPD/httpd-verify.conf"

if httpd -t -f "$TMPD/httpd-verify.conf" 2>&1 | grep -q "Syntax OK"; then
  echo "ALL .htaccess FILES PASS httpd -t"
  exit 0
fi
httpd -t -f "$TMPD/httpd-verify.conf" 2>&1 | grep -v AH00558
echo "HTCACCESS SYNTAX ERRORS PRESENT"
exit 1
