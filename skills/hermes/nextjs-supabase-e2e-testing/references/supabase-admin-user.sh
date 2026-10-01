#!/usr/bin/env bash
# Supabase Admin User Creation Script
# Creates an auto-confirmed test user with specified role (bypasses email verification)

set -euo pipefail

# Usage:
#   ./supabase-admin-user.sh <SUPABASE_URL> <SERVICE_ROLE_KEY> <EMAIL> [ROLE]
#   ./supabase-admin-user.sh "https://xyz.supabase.co" "eyJ..." "qa-admin@test.local" "clinic_admin"

SUPABASE_URL="${1:-}"
SERVICE_ROLE_KEY="${2:-}"
EMAIL="${3:-qa-admin-$(date +%s)@test.local}"
ROLE="${4:-clinic_admin}"

if [[ -z "$SUPABASE_URL" || -z "$SERVICE_ROLE_KEY" ]]; then
  echo "Usage: $0 <SUPABASE_URL> <SERVICE_ROLE_KEY> [EMAIL] [ROLE]"
  echo "Example: $0 'https://cnsuyhmtbqdxsxloyljq.supabase.co' 'eyJ...' 'qa-admin@test.local' 'clinic_admin'"
  exit 1
fi

PASSWORD="Test1234!"
FULL_NAME="QA Admin"

echo "Creating user: $EMAIL (role: $ROLE)"

RESPONSE=$(curl -s -X POST "${SUPABASE_URL}/auth/v1/admin/users" \
  -H "apikey: ${SERVICE_ROLE_KEY}" \
  -H "Authorization: Bearer ${SERVICE_ROLE_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"${EMAIL}\",\"password\":\"${PASSWORD}\",\"email_confirm\":true,\"user_metadata\":{\"full_name\":\"${FULL_NAME}\",\"role\":\"${ROLE}\"}}")

echo "$RESPONSE" | python3 -c "
import sys, json
d = json.load(sys.stdin)
if 'id' in d:
    print(f'✅ Created: {d[\"id\"]}')
    print(f'   Email: {d[\"email\"]}')
    print(f'   Email confirmed: {d.get(\"email_confirmed_at\", \"unknown\")}')
else:
    print(f'❌ Error: {d.get(\"msg\", d.get(\"error_description\", \"unknown\"))}')
    sys.exit(1)
"

echo ""
echo "Login at: https://your-app.vercel.app/auth/login"
echo "Email: $EMAIL"
echo "Password: $PASSWORD"