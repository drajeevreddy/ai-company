#!/usr/bin/env bash
# Apply the app's migrations, in order, against the local Supabase stub.
# Usage: apply_migrations.sh [migrations_dir] [pg_port] [db_name]
set -u
MIG=${1:-$PWD/supabase/migrations}
PORT=${2:-55432}
DB=${3:-endocare}
export PGPASSWORD=${PGPASSWORD:-postgres}
PSQL="psql -h 127.0.0.1 -p $PORT -U postgres -d $DB -v ON_ERROR_STOP=1 -q"

$PSQL -f "$(dirname "$0")/00_supabase_stub.sql" || { echo "STUB FAILED"; exit 1; }
echo "stub: OK"
for f in $(ls -1 "$MIG"/*.sql | sort); do
  if out=$($PSQL -f "$f" 2>&1); then echo "OK    $(basename "$f")";
  else echo "FAIL  $(basename "$f")"; echo "$out" | sed 's/^/        /' | head -6; fi
done
