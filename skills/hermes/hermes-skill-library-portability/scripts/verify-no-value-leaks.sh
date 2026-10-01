#!/usr/bin/env bash
# verify-no-value-leaks.sh — prove no value from a source environment file appears in a finished pack.
#
# A key-shape grep over the source cannot see personal identifiers or machine paths. This checks the
# PACK by VALUE: every value >= MINLEN characters from the source file is grepped across the pack.
#
# Usage:
#   ./verify-no-value-leaks.sh ~/.hermes/.env ~/my-bundle
#   ./verify-no-value-leaks.sh ~/.hermes/.env ~/my-bundle /tmp/values.txt
#
# Exit codes: 0 = no hits, 1 = hits found (triage each), 2 = usage error.
#
# Every hit must be READ, not counted. A hit on a path or a display name is a false positive and
# belongs in the pack README's exclusion note. A hit on a phone number, a WhatsApp @lid / @c.us JID,
# a chat id, an email, or a token-shaped string blocks the handoff until redacted. Re-run after
# redacting: this check is the acceptance test, not the redaction.

set -uo pipefail

SRC="${1:-}"
PACK="${2:-}"
VALS="${3:-/tmp/leak-values.txt}"
MINLEN="${MINLEN:-16}"

if [[ -z "$SRC" || -z "$PACK" ]]; then
  echo "usage: $0 <source-env-file> <pack-dir> [values-file]" >&2
  exit 2
fi
[[ -r "$SRC"  ]] || { echo "cannot read source: $SRC" >&2; exit 2; }
[[ -d "$PACK" ]] || { echo "not a directory: $PACK" >&2; exit 2; }

# Values only, no names. Drop quotes, drop URLs (they are published endpoints, not secrets) and
# drop short strings that would match half the filesystem.
grep -oE '^[A-Za-z_][A-Za-z0-9_]*=.*' "$SRC" \
  | sed 's/^[^=]*=//' \
  | tr -d '"' | tr -d "'" \
  | awk -v n="$MINLEN" 'length($0) >= n' \
  | grep -vE '^https?://' \
  | sort -u > "$VALS"

COUNT=$(wc -l < "$VALS" | tr -d ' ')
echo "values checked: $COUNT (min length $MINLEN)  ->  $VALS"
echo

if [[ "$COUNT" -eq 0 ]]; then
  echo "no values above the length floor; nothing to compare"
  exit 0
fi

HITS=$(grep -rlF -f "$VALS" "$PACK" 2>/dev/null || true)

if [[ -z "$HITS" ]]; then
  echo "CLEAN: no source value appears in $PACK"
  exit 0
fi

echo "HITS — read each one before shipping:"
echo
while IFS= read -r f; do
  [[ -z "$f" ]] && continue
  echo "== $f"
  # print which value matched, so the triage is a glance and not a hunt
  while IFS= read -r v; do
    if grep -qF -- "$v" "$f" 2>/dev/null; then
      printf '   value: %s\n' "$(printf '%s' "$v" | cut -c1-60)"
    fi
  done < "$VALS"
  echo
done <<< "$HITS"

echo "Triage rule: path or display name = false positive, note it in the README."
echo "             identifier, email, phone, JID, chat id, or token = finding, redact and re-run."
exit 1
