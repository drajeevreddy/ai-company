# Hosting a build pack on Replit

Read this when a pack targets Replit. These constraints are read from Replit's own docs and they
change the architecture before any code is written. Verify against docs.replit.com before relying
on any of them; every docs page has a `.md` twin, and `https://docs.replit.com/llms.txt` is the
index (`/features/.../page.md` returns clean markdown).

## The constraint that decides the architecture

`DATABASE_URL` is app-scoped. Replit's own words: the development database "cannot be accessed by
other apps, even ones you own". So a second Repl holding a worker, a queue consumer, or a separate
API service cannot reach the first app's data. Two services means two databases, or an external
Postgres on day one.

Consequence for a pack: specify **one Repl, one process**, with any background work running
in-process. Next.js can boot a worker from `instrumentation.ts` (`register()`, guard on
`process.env.NEXT_RUNTIME === 'nodejs'` and a `WORKER_ENABLED` flag, cache the boot promise against
hot-reload starting several workers). Keep the worker entry point standalone so it can move to a
container host later without a refactor.

## Deployment types, and the one that silently breaks schedulers

| Type | Documented behaviour | Use for |
|---|---|---|
| Autoscale | "scales to zero when idle" | request-driven web apps |
| Static | files from a cache, no backend | marketing pages |
| Reserved VM | "one dedicated server that never sleeps" | queues, cron, anything that must run at a time |
| Scheduled | runs a command on a schedule, then stops | nightly jobs |

A queue consumer on Autoscale misses every job queued while the app is idle, and the symptom is
"nothing published overnight" rather than a crash. Pick Reserved VM (fixed monthly cost) whenever
the pack has a scheduler.

## Database and storage

- Every Repl has a Postgres dev database; 20 GB storage included. One env var: `DATABASE_URL`.
  The legacy Neon vars (`PGHOST`, `PGUSER`, …) are **not** provided on current infrastructure.
- The **production** database is created when you publish, is separate from dev, and the Repl
  Agent cannot modify it. Schema changes reach production by publishing. Therefore migrations must
  run at boot (`prisma migrate deploy` behind a Postgres advisory lock), not by hand.
- App Storage (rename of Object Storage) is GCS-backed, buckets are per project and "cannot be
  shared across apps", and the same bucket set serves the dev and production environments of that
  app. That removes the reason to add R2 or S3.
- Replit's warning: do not rely on files written to a published app's filesystem.

## No managed Redis

Replit lists Replit-managed integrations (databases, auth), connectors (Stripe, Resend, OpenAI),
external integrations (bring your own key) and agent services. Redis is not among the managed ones.
For queues, pg-boss or graphile-worker on the existing Postgres is the lazier and safer choice, and
the transactional enqueue it enables (job row + data row in one commit) is a genuine correctness
win over an external broker.

## Mark as UNVERIFIED in the pack

- The exact `.replit` schema and Nix module names in the target workspace. Generate one in the
  editor and diff it rather than trusting an example.
- Whether a plan allows more than one published app per Project.
- Platform API caps that secondary sources disagree on (see the Instagram daily-publish cap: 25,
  50 and 100 all appear in reachable writing). Never hardcode a cap in a pack; specify reading the
  platform's usage headers and holding below a utilisation threshold.
- Reserved VM sleep behaviour across regions. Add a worker heartbeat to `/readyz` and alert on a gap
  instead of assuming.
