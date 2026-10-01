# Supabase + Vercel tooling gotchas

Small things that cost real hours during [[Projects/DocCare-Security-Remediation]]. Check these before you debug anything else.

## 1. `supabase functions deploy` → "entrypoint path does not exist"
The Docker bundler cannot traverse a `0700` home directory, so bundling fails with an entrypoint error. Fix: bundle server-side, no Docker.
```bash
npx supabase functions deploy <name> --use-api
```

## 2. `vercel env add NAME preview` prompts for a git branch
An interactive prompt that hangs non-interactive runs. Pass the branch positionally or use `--value` + `--yes`:
```bash
vercel env add CRON_SECRET preview --value "..." --yes
# or: vercel env add CRON_SECRET preview <branch>
```

## 3. `vercel env pull` masks secrets
`vercel env pull` returns real values for `NEXT_PUBLIC_*` but `[SENSITIVE]` for secrets (service role, `CRON_SECRET`). Don't assume a pulled `.env` contains the secret. Note that `NEXT_PUBLIC_*` values are already shipped in the client bundle, so they are recoverable from the deployed JS anyway.

## 4. Audit exactly what a real account can see
Public URL + anon key come from the deployed client bundle (or `vercel env pull`). Then use the Auth password grant + PostgREST to see the rows a real user actually reaches:
```bash
curl -s "$SUPABASE_URL/auth/v1/token?grant_type=password" \
  -H "apikey: $ANON_KEY" -H "Content-Type: application/json" \
  -d '{"email":"<user>","password":"<user-supplied-only>"}'
# then, with the returned access_token:
curl -s "$SUPABASE_URL/rest/v1/profiles?select=*" \
  -H "apikey: $ANON_KEY" -H "Authorization: Bearer $ACCESS_TOKEN"
```
No credentials are stored in the vault.

## 5. Vercel Cron auth header
Vercel sends `Authorization: Bearer $CRON_SECRET` automatically when the env var exists. So a cron route that only checks "is a header present" is open when the var is unset — it must **fail closed (401)** when `CRON_SECRET` is missing. Same bug class as the unauthenticated ICS route.

## 6. `supabase db push --linked` hides RAISE NOTICE
`db push` suppresses `RAISE NOTICE` output, so you cannot see what a migration printed. Confirm state separately:
```bash
npx supabase migration list --linked
```

## 7. `supabase config push` writes EVERY key — do not use it to change one setting
`supabase config pull` reads the project config, so it looks like the way to set
an auth setting from the CLI. It is not safe:
- `push` writes the whole file, not a diff. Anything that drifted from the
  template gets reverted too. Here the project had `auth.sms.twilio.enabled = true`
  while the template default is `false` → a push would have silently disabled SMS auth.
- Nested credentials are **masked** by the API (Twilio `account_sid`/`auth_token`,
  Apple client secret) — they appear under "not compared", so the CLI cannot
  round-trip them. Worse, setting `enabled = true` makes `account_sid` a
  *required* field that cannot be filled in, so the file will not even parse.

Use the dashboard, or a Management API
`PATCH /v1/projects/{ref}/config/auth` with a personal access token — that
updates only the named keys. Some settings (leaked-password protection) are not
in the CLI config schema at all and are dashboard/API only.
Always run `supabase config diff` before even considering a push, and do not
commit a `config.toml` that cannot round-trip the masked credentials.

## 8. `vercel env add NAME preview <branch>` cannot target the production branch
`vercel env add CRON_SECRET preview main` fails with *"Cannot set Production
Branch \"main\" for a Preview Environment Variable."* Use a real feature-branch
name, or accept that preview stays unset — which is the safe state when crons
only run in production and the routes fail closed.

See also: [[Skills/devops|devops]] · [[Skills/software-development|software-development]] · [[Skills/rls-verification-harness]]
