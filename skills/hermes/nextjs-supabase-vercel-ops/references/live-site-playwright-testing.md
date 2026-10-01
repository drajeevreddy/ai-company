# Live-site E2E testing of a Next.js + Supabase app with Playwright

Session source: testing https://endocare-gold.vercel.app with a new clinic-admin user.

## Why Playwright

- Hermes browser backend (Camofox at localhost:9377) was not running.
- `computer_use` (`list_windows`/`capture`) returned nothing for the flatpak-sandboxed
  Google Chrome — sandboxed windows are invisible to the X11/AX driver. Don't burn time
  trying to fix the driver; use headless Playwright.

## Setup (no project files touched)

```bash
mkdir -p /tmp/pwtest && cd /tmp/pwtest
npm init -y
npm i playwright
npx playwright install chromium   # "fallback build for ubuntu24.04-x64" warning is fine
```

Sanity check launch, then script the flow. Chromium runs headless without a display.

## Extracting Supabase project URL + anon key from the deployed app

The keys are NOT in the raw HTML — Next.js puts them in JS chunks:

```bash
curl -s https://<site>/auth/login -o /tmp/login.html
for c in $(grep -oE '/_next/static/chunks/[^"]+\.js' /tmp/login.html | sort -u); do
  curl -s "https://<site>$c" -o /tmp/chunk.js
  grep -oE 'https://[a-z0-9]+\.supabase\.co' /tmp/chunk.js && break
done
grep -oE 'eyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+' /tmp/chunk.js | head -1
```

## GoTrue auth reality checks (before writing test users)

```bash
# does the project require email confirmation?
curl -s "${URL}/auth/v1/settings" -H "apikey: $ANON"   # -> mailer_autoconfirm: true/false
```

- `mailer_autoconfirm: false` (the default) means email signups are created with
  `confirmation_sent_at` set and NO session. You cannot log in without clicking the emailed
  link, and there is no inbox access.
- Signup response shapes: with confirmation ON, the response is a FLAT user object
  (`{"id":..., "confirmation_sent_at":..., "identities":[...]}`) — no session fields.
- Repeated signup probes hit Supabase email send rate limits: HTTP 429
  `{"code":429,"error_code":"over_email_send_rate_limit","msg":"email rate limit exceeded"}`
  — blocks real testing for roughly an hour. Probe sparingly.

## Unblocking demo-user creation

Ordered by reliability:
1. **Service-role key** (Settings → API): admin API, `createUser({email, password,
   email_confirm: true, user_metadata: {role: 'clinic_admin'}})` — instant confirmed user,
   no email sent, no rate limit. Best path.
2. User disables "Confirm email" (Supabase → Auth → Providers → Email). Note the settings
   endpoint may lag the toggle; verify by actually signing up and checking for a session,
   not by re-reading the settings flag.
3. User creates + confirms the account themselves and shares credentials.

Signup UI (doccare): email + password + role Select (includes `clinic_admin`),
`emailRedirectTo: /auth/verify`. Middleware gates all /app routes behind a session, so
nothing meaningful is testable logged-out.

## Cleanup hygiene

Unconfirmed probe accounts (`qa-*@testmail.com`) linger in Auth → Users; harmless but tell
the user they exist so they can delete them.
