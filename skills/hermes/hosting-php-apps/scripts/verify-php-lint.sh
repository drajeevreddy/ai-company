# Verify PHP Lint (static binary fallback)

#!/usr/bin/env bash
# php -l sweep on all PHP files in a project, using Docker if no host PHP
# Usage: verify-php-lint.sh <project-dir> [subdirs...]

set -euo pipefail
PROJECT="${1:-.}"
shift || true
SUBDIRS=("$@")

# Try host PHP first
if command -v php >/dev/null 2>&1; then
    PHP_CMD="php"
else
    # Use container if project is Docker-hosted
    CONTAINER=$(docker ps --format '{{.Names}}' | head -1)
    if [ -n "$CONTAINER" ]; then
        PHP_CMD="docker exec $CONTAINER php"
    else
        # Static PHP CLI fallback
        STATIC_PHP="/tmp/php-static/php"
        if [ ! -x "$STATIC_PHP" ]; then
            mkdir -p /tmp/php-static
            curl -fsSL "https://dl.static-php.dev/static-php-cli/bulk/php-8.3.14-cli-linux-x86_64.tar.gz" | tar -xzf - -C /tmp/php-static
        fi
        PHP_CMD="$STATIC_PHP"
    fi
fi

FAIL=0
while IFS= read -r f; do
    if ! $PHP_CMD -l "$f" 2>&1 | grep -q "No syntax errors"; then
        echo "FAIL $f"
        $PHP_CMD -l "$f" 2>&1 | tail -3
        FAIL=1
    fi
done < <(find "$PROJECT" -name '*.php' -not -path '*/.git/*' -not -path '*/vendor/*' | sort)

[ $FAIL -eq 0 ] && echo "ALL $(find "$PROJECT" -name '*.php' -not -path '*/.git/*' -not -path '*/vendor/*' | wc -l) PHP files lint clean"