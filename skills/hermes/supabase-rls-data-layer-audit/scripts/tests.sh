#!/usr/bin/env bash
# Role-impersonation tests. Usage: tests.sh [pg_port] [db_name]
set -u
PORT=${1:-55432}
DB=${2:-endocare}
export PGPASSWORD=${PGPASSWORD:-postgres}
P="psql -h 127.0.0.1 -p $PORT -U postgres -d $DB -q -A -t"

$P -c "GRANT USAGE ON SCHEMA public TO anon, authenticated, service_role;" \
   -c "GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated, service_role;" \
   -c "GRANT SELECT ON ALL TABLES IN SCHEMA public TO anon;" \
   -c "GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO anon, authenticated, service_role;"

as_role () { # $1=role $2=uid-or-empty $3=label $4=sql
  echo "--- $3"
  if [ -n "$2" ]; then CLAIMS="{\"sub\":\"$2\",\"role\":\"$1\"}"; else CLAIMS="{\"role\":\"$1\"}"; fi
  $P <<SQL 2>&1 | sed 's/^/    /'
SET ROLE $1;
SET request.jwt.claims = '$CLAIMS';
$4
SQL
}

A=${A:-aaaaaaaa-0000-0000-0000-000000000001}
B=${B:-bbbbbbbb-0000-0000-0000-000000000002}
ADMIN=${ADMIN:-cccccccc-0000-0000-0000-000000000003}
ATTACKER=${ATTACKER:-dddddddd-0000-0000-0000-000000000004}
Q_B=${Q_B:-22222222-2222-2222-2222-222222222222}

as_role authenticated $A "staff A reads patients"            "SELECT count(*) FROM public.patients;"
as_role authenticated $B "staff B reads patients"            "SELECT count(*) FROM public.patients;"
as_role authenticated $ATTACKER "self-registered super_admin reads everything" "SELECT (SELECT count(*) FROM public.patients), (SELECT count(*) FROM public.clinic_staff);"
as_role anon "" "anon (kiosk path) inserts a patient"       "INSERT INTO public.patients (first_name,last_name,date_of_birth) VALUES ('X','Y','1990-01-01');"
as_role authenticated $ADMIN "admin A rewrites another tenant's patient" "UPDATE public.patients SET phone='+910000000000' WHERE clinic_id='$Q_B';"
as_role authenticated $A "staff A cancels another tenant's appointments" "UPDATE public.appointments SET status='cancelled' WHERE clinic_id='$Q_B';"

 echo "--- double booking: three inserts into the same doctor/slot"
$P <<SQL 2>&1 | sed 's/^/    /'
INSERT INTO public.appointments (patient_name, appointment_date, start_time, end_time, doctor_name, type, title, status)
VALUES ('P1', CURRENT_DATE, '10:00','10:30','Dr A','consultation','dup-1','scheduled'),
       ('P2', CURRENT_DATE, '10:00','10:30','Dr A','consultation','dup-2','scheduled'),
       ('P3', CURRENT_DATE, '10:15','10:45','Dr A','consultation','dup-3','scheduled');
SELECT 'overlapping rows accepted: ' || count(*) FROM public.appointments
 WHERE doctor_name='Dr A' AND appointment_date=CURRENT_DATE AND start_time < '10:30' AND end_time > '10:00';
SELECT indexdef FROM pg_indexes WHERE tablename='appointments';
SQL
