#!/usr/bin/env bash
# Install a Hermes skill pack into a profile. Copy and adjust per pack.
#
#   ./install.sh                 # install into ~/.hermes (default profile)
#   ./install.sh myprofile       # install into ~/.hermes/profiles/myprofile
#   ./install.sh --merge         # keep existing skills, only add missing ones
#
# Non-destructive by default: an existing skills/ tree is moved aside to
# skills.bak.<timestamp> before extraction.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ARCHIVE="$HERE/hermes-skills.tar.gz"
MODE="replace"
PROFILE=""

for arg in "$@"; do
  case "$arg" in
    --merge) MODE="merge" ;;
    -h|--help) sed -n '2,10p' "$0"; exit 0 ;;
    *) PROFILE="$arg" ;;
  esac
done

if [[ ! -f "$ARCHIVE" ]]; then
  echo "error: $ARCHIVE not found — run this script from inside the export folder." >&2
  exit 1
fi

if [[ -n "$PROFILE" ]]; then
  SKILLS_DIR="$HOME/.hermes/profiles/$PROFILE/skills"
else
  SKILLS_DIR="$HOME/.hermes/skills"
fi

EXPECTED=${EXPECTED_SKILLS:-343}   # set to the pack's SKILL.md count
mkdir -p "$SKILLS_DIR"

if [[ "$MODE" == "replace" && -n "$(ls -A "$SKILLS_DIR" 2>/dev/null)" ]]; then
  BACKUP="$SKILLS_DIR.bak.$(date +%Y%m%d_%H%M%S)"
  echo "existing skills found -> moving to $BACKUP"
  mv "$SKILLS_DIR" "$BACKUP"
  mkdir -p "$SKILLS_DIR"
fi

echo "extracting into $SKILLS_DIR"
tar xzf "$ARCHIVE" -C "$SKILLS_DIR"

FOUND=$(find -L "$SKILLS_DIR" -name SKILL.md | wc -l)
echo "SKILL.md files found: $FOUND (archive holds $EXPECTED)"

if [[ "$FOUND" -lt "$EXPECTED" ]]; then
  echo "warning: fewer skills than expected — the extract may be incomplete." >&2
  exit 1
fi

echo
echo "done. Next steps:"
echo "  1. restart Hermes (a running session keeps its old skill list)"
echo "  2. run:  hermes skills list | head -50"
echo "  3. read: $HERE/INSTALL.md  (what needs installing on top of the raw skills)"
