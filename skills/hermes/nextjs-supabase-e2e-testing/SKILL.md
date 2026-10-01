---
name: nextjs-supabase-e2e-testing
description: E2E test/debug patterns for Next.js 15 + Supabase EMR apps — authenticated browser QA, session-cookie import, data-layer write verification, deployed-revision checks, date/timezone fixes.
---

# Next.js + Supabase E2E Testing & Debugging Patterns

## Trigger
Use when testing, debugging, or deploying a Next.js 15 application backed by Supabase (PostgreSQL + Auth + Realtime), especially EMR/EHR, clinic management, or dashboard-style SaaS apps. Also load this when asked to "test <deployed url> end to end" with one account's login: §3 gets you in without the password and §4 is the evidence standard.

---

## 0. Before you fix anything: find the source and the deployed revision

**The workspace you were dropped in is not necessarily the app.** A directory named after the project can hold a completely unrelated codebase; editing there wastes the whole session and produces diff noise the user never asked for. Locate the repo that owns the deployment first:

```bash
# the Supabase project ref and the production domain both appear in the real repo
search_files pattern="<supabase-project-ref>|<prod-domain>" target=content path=~
find ~ -maxdepth 6 -type d -name "<a-route-dir-from-the-app>" -not -path "*/node_modules/*"
```

Then establish which copy is canonical and how far it sits from production:

```bash
git status --short && git log --oneline -5                 # repeat in EVERY candidate copy
git rev-list --left-right --count origin/main...HEAD       # "0  23" = 23 commits undeployed
ls *.md docs/ 2>/dev/null                                  # MASTER-PROMPT / REPORT / DEPLOYMENT name the copy to work in
```

Sibling copies exist because one of them is stale: duplicate migration files across copies poison `supabase migration list`, and a repo doc usually says explicitly which copy to edit and which to leave alone. Read those docs before touching anything.

**Confirm what the live URL actually serves before diagnosing it.** A deployed build can lag the repo by dozens of commits while the database is migrated *ahead* of that build, which produces symptoms that make no sense from either side alone — a feature that works in the repo and not in production, a column the deployed code writes that the repo never creates, bugs already fixed in the working copy. Check both sides:

```bash
vercel inspect https://<prod-domain>        # Aliases block → does the domain point at the build you think?
npx supabase migration list --linked        # local vs remote migrations must match
```

A finding is only a finding against a build you can prove is live. Report repo-vs-production drift as its own line — "already fixed in the repo, N commits undeployed" is often the most useful sentence in the report, and it stops you from re-fixing work that exists.

---

## 1. Build Verification Gate (Required Before Deploy)

**Always run all three locally before pushing:**

```bash
# 1. TypeScript check
npx tsc --noEmit

# 2. Production build (requires placeholder env for static generation)
NEXT_PUBLIC_SUPABASE_URL=https://placeholder.supabase.co \
NEXT_PUBLIC_SUPABASE_ANON_KEY=placeholder-anon-key \
SUPABASE_SERVICE_ROLE_KEY=placeholder-service-role-key \
npm run build

# 3. Lint (ESLint flat config, not deprecated `next lint`)
npm run lint
```

**Why placeholder env?** Pages that instantiate Supabase clients at build time (e.g., `/portal`, `/reminders`) will fail with "@supabase/ssr: Your project's URL and API key are required" during static generation. The placeholder values satisfy the client constructor without hitting real APIs.

When the task is "fix and test", the gate is not done at a green build — landing the fix is part of the job:

```bash
vercel --prod --yes                                          # non-interactive, from the linked dir
vercel inspect https://<prod-domain>                          # Aliases block must list the new deployment id
```

Then re-run the live checks against the production URL, not a preview. A fix that only exists locally does not fix the user's problem — and a preview URL skips the alias, so you cannot claim the live app changed.

### When the CI check on the push is red

Read the failing run before editing anything: `gh run list --limit 5` then `gh run view <id> --log-failed`. A job that passes locally and fails on a fresh runner is timing or environment, not SQL — and the suite's own `FATAL: <migration>.sql did not apply cleanly` line names a gate, not the cause (it dumps the whole apply log under it; the first non-`OK` line is the real state).

The containerised-Postgres trap in that log: an in-container `docker exec pg_isready` reports ready against the temporary server the official image runs on the unix socket during initdb, so the first client through the published port is accepted by docker-proxy and then cut off — `server closed the connection unexpectedly`. Probe readiness with a round-trip through `127.0.0.1:$PORT` instead, and verify a harness fix against a **destroyed** container: a warm container hides every cold-start race.

Full recipe — the readiness loop, container-state diagnostics for gate failures, and the push-and-prove order for a new schema invariant: `references/ci-rls-suite.md`.

---

## 2. Playwright Test Patterns for EMR/EHR Apps

### Test User Creation (Service-Role Key)
```bash
# Create auto-confirmed clinic_admin user (no email verification needed)
SUPABASE_URL="https://<ref>.supabase.co"
SERVICE_ROLE_KEY="eyJ..."
EMAIL="qa-admin-$(date +%s)@test.local"
curl -X POST "${SUPABASE_URL}/auth/v1/admin/users" \
  -H "apikey: ${SERVICE_ROLE_KEY}" \
  -H "Authorization: Bearer ${SERVICE_ROLE_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"${EMAIL}\",\"password\":\"Test1234!\",\"email_confirm\":true,\"user_metadata\":{\"full_name\":\"QA Admin\",\"role\":\"clinic_admin\"}}"
```

### Comprehensive Module Test Checklist
Test every route that exists in the sidebar navigation:
- `/dashboard` — stats cards, data widgets
- `/appointments` — calendar/week view, New Appointment dialog
- `/patients` — list, create (`/patients/new`)
- `/queue-board` — patient queue
- `/prescriptions` — list
- `/laboratory` — orders/results
- `/pharmacy` + `/pharmacy/history` — stock, dispensing
- `/portal` — patient-facing documents
- `/consultation` — SOAP notes
- `/doctors/schedule` — availability grid
- `/settings` — tabs: Doctors, Reminders, Billing, etc.
- `/analytics` — charts
- `/billing` — invoices
- `/kiosk` — check-in
- `/reminders` — scheduled

### Selector Strategy for shadcn/ui + Custom Components
```javascript
// Input components generate IDs from label text: "First Name *" → "first-name-*"
await page.fill('input[id^="first-name-"]', 'Value');

// Dialogs: custom component (not Radix) — look for overlay
const dialog = await page.$('.fixed.inset-0.z-50, [role="dialog"]');

// Buttons by text content
await page.click('button:has-text("New Appointment")');
```

---

## 3. Getting an authenticated session without the password

Never type the account password into a login form — the vault tools own that field. If no vault item exists for the origin and `browser_vault_save_login` refuses the page (`Open the site's login page first`, even though you are on it), do NOT ask the user for the password. Reuse the session their own browser already has.

Full recipe: `references/session-cookie-import.md`. One-shot helper: `scripts/import_browser_session_cookie.py`.

Shape of it: decrypt the `sb-<ref>-auth-token` cookie out of the user's real Chrome/Chromium store (keyring secret → PBKDF2-HMAC-SHA1 → AES-128-CBC; the decrypted plaintext is 32 bytes of Chrome preamble followed by the actual value), then import it into the live headless context with the Camofox endpoint `POST /sessions/<userId>/cookies` using Playwright cookie objects. `<userId>` comes from `/health` → `activeUserIds` read straight after a browser tool call, and a tab must already exist for that user. Verify by loading a protected route and asserting the app shell (sidebar + user chip) renders, not just a 200.

Base64-decode the same cookie value to get the user's `access_token` — that token is what makes the §4 probes possible. Treat it as ~1h of life; refresh it rather than re-deriving the cookie:

```bash
curl -s "${SUPABASE_URL}/auth/v1/token?grant_type=refresh_token" \
  -H "apikey: ${ANON}" -H "Content-Type: application/json" \
  -d "{\"refresh_token\":\"${REFRESH_TOKEN}\"}"      # → new access_token AND a rotated refresh_token; persist both
```

A 401 from PostgREST mid-session is this expiry, not a broken probe.

Two things reset the session mid-task, and both look like "the app logged me out": the cookie jar is scoped to the live browser session, so re-import whenever `/health` reports a different entry in `activeUserIds`; and the app's own middleware clears the cookie when the token is past `expires_at`. Re-import the cookie and reload the protected route before re-running checks.

## 4. Verify every write at the data layer

**The UI is not evidence.** A toast, an optimistic row, a `History (1)` counter and a bumped stat card all render without a successful INSERT. After every mutating action, query the table with the signed-in user's `access_token` and assert the row:

```bash
curl -s "${SUPABASE_URL}/rest/v1/<table>?select=*" -H "apikey: ${ANON}" -H "Authorization: Bearer ${TOKEN}"
```

- **Page names are not table names.** Probe candidates with `?select=*&limit=1` and read the `PGRST205` hint — it names the real table (`consultations` → `soap_notes`, `laboratory_orders` → `lab_orders`, `reminders` → `auto_reminder_logs`). Never report "data was lost" before you find the table it actually landed in. `scripts/probe_supabase_tables.py` does the sweep.
- **Run the reject paths, not just the happy path.** For every form: empty submit (expect a visible error AND zero new rows), duplicate submit (expect an update or a rejected duplicate, never a second row for the same logical record), re-save of a draft (must UPDATE the existing row — a second INSERT is a finding), and boundary values (negative, zero, absurdly large). The app accepting `bp_systolic: 1309999` with no message is a finding; so is an empty submit that silently does nothing.
- **Separate "the handler never ran" from "the write failed".** Check `document.elementFromPoint()` at the button centre first; then trigger the node's own `.click()`; then look for the row. A dead handler, an intercepted pointer and a rejected write each need different evidence.
- **Denormalised columns betray missing links.** If a created row has `doctor_id: null` next to `doctor_name: "Dr. Gupta"`, or `appointment_id: null` on a queue/SOAP row, the FK is decorative — per-doctor and per-visit reporting is already broken. Check the FK columns, not just the row count.
- **Report shape:** severity-ordered findings, each with the table + row evidence and a repro; then list the test records you created with their ids so they can be deleted.

## 5. Harness pitfalls that look like app bugs

- **A snapshot with an empty `main` is not a blank page.** Client-rendered detail routes wrap content in a fade-in element, so the accessibility snapshot shows nothing while the DOM is populated. Re-read `document.querySelector('main').textContent` after a few seconds before filing a blank screen.
- **Empty states and `— Loading…` are pre-fetch states.** `No appointments today`, `No patients in the queue yet`, `0` stat cards resolve to real values ~10s later. Do not file them as wrong data; file the missing loading state.
- **Re-read the field value after typing.** Into a numeric input, typed text can append instead of replace (`130` + `9999` → `1309999`). A corrupted stored value may be the harness. Confirm the field held what you intended before reporting it, and never leave the claim ambiguous.
- **Record the harness timezone before any date finding** (`Intl.DateTimeFormat().resolvedOptions().timeZone`, `new Date().toString()`). A day-off date or a wrong clock on a wall-mounted display is only a finding once you know the browser TZ and the server's date differ from the app's.
- **Refs drift after every re-render.** Re-snapshot immediately before the click; a stale ref can land on a neighbouring control (a `Today` click landing a day off in a date strip, a `Schedule` ref dispatching on a `<select>`). Confirm the click's effect, not the tool's success field.

  Disambiguate with a capture-phase listener instead of guessing — this is the difference between "the control is dead" and "my click never reached it":

  ```js
  window.__clicks = [];
  document.addEventListener('click', e => window.__clicks.push({ tag: e.target.tagName, text: (e.target.innerText || '').slice(0, 30) }), true);
  // click the ref, then read window.__clicks
  ```

  If the recorded target is not the control you meant, the harness mis-targeted: re-snapshot and retry, or drive the node's own `.click()` to exercise the handler. Never file a dead-button bug on a click you cannot show landed on the button.
- **Do not instrument `window.fetch` to capture app traffic in a Next.js/Supabase app.** The router and supabase-js capture a fetch reference at module init, so the patched wrapper sees nothing and you will wrongly conclude "no request was made". The table state from §4 is the source of truth.
- Console log capture is unavailable on the Camofox backend (`browser_console` returns a note, not messages). Build evidence from DOM text, screenshots and PostgREST queries instead of waiting on console output.

---

## 6. Common Fixes & Pitfalls

### Dialog Button Doesn't Respond
**Symptom:** Clicking "Schedule"/"Submit" in a dialog does nothing; Playwright reports "label intercepts pointer events".

**Root Cause:** Custom Dialog component's content wrapper missing `z-50`, so the backdrop or label elements sit above footer buttons.

**Fix** (`src/components/ui/dialog.tsx`):
```tsx
<div className={cn("relative z-50 w-full max-w-lg ...", className)}>
```
The `relative z-50` on the content wrapper (not just the overlay) ensures buttons are above all labels/backdrop.

**Before blaming the dialog, disambiguate:** the same symptom appears when the harness's synthetic click misses. `document.elementFromPoint()` at the button centre returning the button itself means nothing is covering it — then trigger the node's `.click()` and check whether the write lands (§4). Interception, a dead handler and a rejected write all look identical from the outside.

### Date-Only Values Shift By A Day
**Symptom:** the calendar highlights the right day while the heading beside it names the previous one; invoices and appointments land on yesterday; "today" filters go empty in the early morning.

**Two root causes, both one-liners, both invisible to a user ahead of UTC:**

```ts
new Date("2026-09-13")                     // parsed as UTC midnight → renders Sep 12 in every TZ west of UTC
new Date().toISOString().split("T")[0]     // UTC "today" → reports yesterday between 00:00 and 05:30 IST
```

Fix date-only strings once, in the formatter, rather than at each call site:

```ts
export function toLocalDate(d: string | Date): Date {
  if (typeof d === "string") {
    const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(d.trim());
    if (m) return new Date(Number(m[1]), Number(m[2]) - 1, Number(m[3]));
  }
  return new Date(d);
}
// plus a localDateKey(d = new Date()) returning a local YYYY-MM-DD, never via toISOString
```

Then `grep -rn 'toISOString().split("T")' src/` and convert every hit. The holders of a UTC "today" are always the same set: invoice/record `date` fields, analytics month ranges, reminder horizons, "upcoming" filters on list pages, and `min` on date inputs. Same class of bug hides in locale helpers that shadow the shared formatter — grep the helper name, not just the util.

### Draft Re-Saves Must Update, Not Insert
A save handler that always INSERTs leaves a duplicate per press and a stale draft sitting next to its completed version. Resolve the open record first, then branch:

```ts
const { data: openDraft } = await db.from("soap_notes").select("id")
  .eq("patient_id", id).eq("status", "draft")
  .order("created_at", { ascending: false }).limit(1).maybeSingle();
// openDraft ? .update(payload).eq("id", openDraft.id) : .insert([payload])
```

Promote that same row on Complete so a draft never survives beside its completed twin. Application-level resolution is a habit; a partial unique index on the open record makes it a guarantee.

### Bound Numeric Clinical Fields
Free `type="number"` inputs store anything a typo produces. Put the plausible ranges in one map, mirror them as `min`/`max`, render the message inline, and refuse the save naming the offending field. Validation that only surfaces as a database error reaches the clinician as a generic failure, and a saved `pulse: -50` is worse than a rejected one.

### Query-Param Deep Linking (`?new=true`)
**Pattern:** Sidebar quick actions use `/appointments?new=true` to auto-open dialogs.

**Implementation** in page component:
```tsx
import { useSearchParams } from 'next/navigation';

const searchParams = useSearchParams();
useEffect(() => {
  if (searchParams.get('new') === 'true') {
    setFormDate(selectedDate);
    setShowNewAppointment(true);
  }
}, [searchParams]);
```

### Vercel Hobby Plan Cron Constraint
**Error at deploy:** "Cron job runs more than once per day" (rejected at deploy time).

**Fix** in `vercel.json`:
```json
{
  "crons": [
    { "path": "/api/cron/process-reminders", "schedule": "0 9 * * *" }
  ]
}
```
Only `@daily` or `0 9 * * *` (once daily) allowed on Hobby. Remove any `*/30 * * * *` or hourly schedules.

### Supabase RLS + Profile Creation
**Symptom:** User authenticates but middleware redirects to `/auth/login` (no profile row).

**Check:** `profiles` table must have a row for the `auth.users` ID with correct `role`. Service-role key can verify:
```bash
curl "${SUPABASE_URL}/rest/v1/profiles?select=*" \
  -H "apikey: ${SERVICE_ROLE_KEY}" -H "Authorization: Bearer ${SERVICE_ROLE_KEY}"
```

---

## 7. Debugging Checklist (When Things Go Wrong)

| Symptom | First Check |
|---------|-------------|
| Build fails on `/portal`, `/reminders` | Missing placeholder `.env.local` |
| Login works but redirects to `/auth/login` | Missing `profiles` row for user |
| Dialog buttons unclickable | Missing `z-50` on dialog content |
| `?new=true` doesn't open dialog | `useSearchParams` effect missing |
| Vercel deploy fails on cron | Schedule > once/day on Hobby plan |
| 404 on `/doctors` | No `page.tsx` — use `/doctors/schedule` |
| Page looks blank in a snapshot | Client-rendered detail route mid-fade — read `main.textContent`, see §5 |
| A bug you "fixed" is still live | Undeployed commits or a stale alias — `vercel inspect`, §0 |
| Heading/day strip disagree with the calendar | Date-only string parsed as UTC, or a `toISOString()` "today" — §6 |
| Second identical row after re-saving a draft | Handler INSERTs unconditionally — §6 |
| Submit "does nothing" | `elementFromPoint` at the button centre, then the node's `.click()`, then the table (§4) |
| Row missing after a "saved" toast | Wrong table name — read the `PGRST205` hint (§4) |

---

## 8. Things that make automation lie to you

| Symptom | Reality |
|---------|---------|
| A dialog/buttons click "does nothing" | Camofox's snapshot ref can map to the wrong node (a click aimed at Schedule landed on a `<select>`). Arm `document.addEventListener('click',…,true)` first, then click: the recorded target tells you whether the app or the ref mapping is at fault. `element.click()` on the resolved node works when the ref does not. |
| "No feedback on submit" | Sonner toasts auto-dismiss in ~4s, so a DOM read after the fact shows an empty toaster. Attach a `MutationObserver` on the toaster and read the log, or you will report working validation as a silent failure. |
| A page renders its empty state on first read | These pages fetch client-side and can take ~10s; `innerText` right after navigation shows "No X today". Wait, re-read, and confirm against the table over REST before calling it a bug. |
| 500 on a server action, page shows empty | `grep '"level":"error"'` in `vercel logs --json` names the real cause (e.g. `AuthError: Staff access required` from a stale access token). `.catch(() => setLoading(false))` turns that failure into "no data" — check the logs before trusting an empty panel. |
| A delete/destructive button click "does nothing" | A native `confirm()` dialog is open and blocking — automation cannot see or dismiss it, so the click looks like a silent no-op. Grep the component for `confirm(` before filing it as broken; then verify the DELETE endpoint directly with an authenticated curl (login → cookie jar → `DELETE /api/…?id=…`) and confirm the row is gone at the data layer. |

## 9. Vercel preview deployments: env vars are per-environment

`vercel env ls` lists every variable with the environments it belongs to. A Supabase app whose variables exist **only** under Production builds production fine and fails every preview/PR build at prerender:

```
Error occurred prerendering page "/auth/forgot-password"
Error: @supabase/ssr: Your project's URL and API key are required to create a Supabase client!
```

Set the public vars for preview (`vercel env add NEXT_PUBLIC_SUPABASE_URL preview --value ...`), plus the service-role key when preview runtime needs the admin client. Check what the app actually reads first (`grep -rn "process.env" src/`) — mirroring the whole production list usually adds unused names.

`vercel env pull` masks every value as `[SENSITIVE]`, so production values cannot be copied out of Vercel. Recover them from the provider's own CLI — `npx supabase projects api-keys --project-ref <ref> --reveal --output-format json`, redirected to a file so no secret reaches stdout — and cross-check one against a value already in the live bundle to prove you are wiring the right project.

Previews sit behind Deployment Protection: plain `curl` gets a 302 to the SSO page and `-L` returns *that* page's 200, which reads as a pass. Use `vercel curl` to reach the app itself, then confirm anonymous access still fails closed (`{"error":"Unauthorized"}` from `/api/cron/*`).

## 10. Reference Files

- `references/playwright-emr-test.js` — Full comprehensive test script (copy and adapt)
- `references/placeholder-env.example` — Build-time env template
- `references/supabase-admin-user.sh` — Service-role user creation script
- `references/session-cookie-import.md` — Reuse the user's existing browser session instead of a password (§3)
- `references/ci-rls-suite.md` — Run the RLS acceptance suite; read a red CI check; cold-start readiness race in containerised Postgres (§1)
- `scripts/import_browser_session_cookie.py` — Decrypt + import that session cookie into the live headless context
- `scripts/probe_supabase_tables.py` — Probe which tables exist and which are empty, before any data-layer verdict (§4)

---

## Related Skills
- `supabase-nextjs-debugging` — Silent write failures, RLS, middleware
- `vercel-deployment-troubleshooting` — Failing Vercel deployments
- `gstack-qa` — Systematic QA testing workflow