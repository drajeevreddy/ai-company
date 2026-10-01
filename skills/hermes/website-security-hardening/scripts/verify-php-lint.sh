#!/usr/bin/env bash
# php -l sweep for a PHP project using a REAL PHP binary.
# If `php` isn't installed (and sudo isn't available to install it), this
# downloads a static PHP CLI build — no root needed.
#
# Usage:
#   verify-php-lint.sh <project-dir> [dir1 dir2 ...]
#   (default dirs: <project-dir> itself)
#
# Exit 0 if every PHP file passes `php -l`, 1 otherwise.
set -u

PROJ="${1:?usage: verify-php-lint.sh <project-dir> [dirs...]}"
shift
DIRS=("$@")
[ ${#DIRS[@]} -eq 0 ] && DIRS=("$PROJ")

# Locate or fetch a PHP binary
PHP="$(command -v php || true)"
if [ -z "$PHP" ]; then
  PHP=/tmp/hermes-php/php
  if [ ! -x "$PHP" ]; then
    echo "No php found; downloading static PHP 8.3 CLI..." >&2
    mkdir -p /tmp/hermes-php
    curl -sL -o /tmp/php-static.tar.gz \
      https://dl.static-php.dev/static-php-cli/bulk/php-8.3.14-cli-linux-x86_64.tar.gz
    tar -xzf /tmp/php-static.tar.gz -C /tmp/hermes-php
    rm -f /tmp/php-static.tar.gz
  fi
fi
echo "Using: $($PHP -v | head -1)" >&2

fail=0
count=0
while IFS= read -r f; do
  count=$((count+1))
  if ! "$PHP" -l "$f" >/dev/null 2>&1; then
    echo "FAIL  $f"
    "$PHP" -l "$f" 2>&1 | tail -1
    fail=1
  fi
done < <(find "${DIRS[@]}" -name "*.php" -type f 2>/dev/null)

echo "Linted $count PHP file(s)."
if [ "$fail" -eq 0 ]; then
  echo "ALL PHP FILES PASS php -l"
  exit 0
fi
echo "SYNTAX ERRORS PRESENT"
exit 1
