# The repo's own RLS acceptance suite: running it, and reading it when CI is red

Applies to the `tests/rls/` harness pattern: `up.sh` starts a throwaway
`postgres:<major>-alpine` container on a non-default port, `apply.sh` applies the
Supabase stub plus **every** migration to a fresh database (reporting OK/FAIL per
file and continuing past failures), `grants.sql` + `seed.sql` add Supabase-equivalent
privileges and two tenants, and `run.sh` asserts isolation by `SET ROLE anon` /
`authenticated` with a forged `request.jwt.claims`. `run.sh` gates on the migrations
the assertions depend on, so a suite failure can mean "the SQL is wrong" **or**
"the server died" — distinguish before editing anything.

## Read the failing run before touching code

```bash
gh run list --limit 5                 # id, status, workflow, branch, duration
gh run view <id> --log-failed         # the failing step's full log
gh run view <id>                      # which jobs/steps passed; annotations are warnings
```

`gh` needs an authenticated session (`gh auth status`). CI-only failures on a
`ubuntu-latest` runner that pass locally are almost always timing or environment,
not SQL — read the first non-`OK` line of the apply log, don't skim for the
google-able phrase.

## The cold-start readiness race (and the fix)

**Symptom.** First CI run on a branch dies seconds in:

```
### 0b. apply stub + all migrations (must be a clean run)
FATAL: <some_migration>.sql did not apply cleanly:
    STUB FAILED
    psql: error: connection to server at "127.0.0.1", port 55440 failed:
      server closed the connection unexpectedly
```

The named migration is a red herring: that gate only reports the first expected
migration whose `OK` line is missing, and the block dumps the *entire* apply log.
The body's first line is the real state.

**Mechanism.** Waiting with an in-container probe (`docker exec $NAME pg_isready`)
is wrong. The official image runs a **temporary server on the unix socket** while it
initialises, so the probe answers "ready" ~1s after `docker run` — before the real
server listens on TCP. The next client connects through the published port,
docker-proxy accepts the TCP connection, finds no backend, and the client sees
`server closed the connection unexpectedly`. A warm local container skips initdb
entirely, which is why this only ever shows up on a cold runner.

**Fix — probe the path the suite actually uses.** A round-trip through the
published port can only succeed once the real server is serving:

```bash
printf 'waiting for Postgres to accept TCP connections on 127.0.0.1:%s' "$PORT"
ready=0
for _ in $(seq 1 60); do
  if PGPASSWORD="$PW" psql -h 127.0.0.1 -p "$PORT" -U postgres -d postgres -tAc 'select 1' >/dev/null 2>&1; then
    ready=1; break
  fi
  # a container that died must not look like a slow start
  if [ "$(docker inspect -f '{{.State.Running}}' "$NAME" 2>/dev/null)" != "true" ]; then
    echo; echo "ERROR: container '$NAME' exited before Postgres became reachable." >&2
    docker inspect -f 'ExitCode={{.State.ExitCode}} OOMKilled={{.State.OOMKilled}}' "$NAME" >&2 || true
    docker logs --tail 40 "$NAME" >&2 || true
    exit 1
  fi
  printf '.'; sleep 1
done
```

**Prove the fix on a cold container.** `npm run test:rls:down` (or `docker rm -f`)
first, then run the suite: a pass against a warm container is not evidence, and the
readiness loop should visibly wait a few seconds instead of reporting ready
instantly.

## Make a gate failure self-explaining

When a migration gate trips, print the container's own state — a dead server and a
bad migration are indistinguishable in the apply log:

```bash
container_state() {
  docker ps -a --format '{{.Names}}' | grep -qx "$NAME" || return 0
  { echo "--- container '$NAME' state (a dead server is not a SQL error) ---"
    docker inspect -f 'Running={{.State.Running}} ExitCode={{.State.ExitCode}} OOMKilled={{.State.OOMKilled}}' "$NAME" 2>/dev/null
    docker logs --tail 40 "$NAME" 2>/dev/null
  } >&2
}
```

Call it from each `FATAL:` gate before `exit 1`.

## Pairing a schema change with the suite

When the migration adds an invariant (see `supabase-project-operations` §4), the
suite is where it gets proved. Order: dedupe existing rows → create the index →
handle the loser in the app (`23505`) → `db push --linked --dry-run` → `db push
--linked` → re-run `migration list --linked` → probe production over REST for all
three directions (duplicates gone, second open insert refused, finished row still
accepted).
