---
name: ai-routing-gateway
description: "Install local AI routing gateway (OmniRoute) inside Hermes."
---

# AI Routing Gateway Setup

Class-level skill for installing and configuring local AI routing/proxy gateways inside Hermes. Currently covers **OmniRoute** as the primary example, but the workflow generalizes to any similar tool.

## What This Covers

- Cloning and installing the gateway from source
- Fixing known migration/schema collisions
- Resolving missing native dependencies (better-sqlite3, etc.)
- Configuring `.env` secrets and admin credentials
- Starting the dev server and verifying it works
- Exposing the MCP endpoint for Hermes agent integration
- Setting up as a persistent systemd user service

## OmniRoute-Specific Setup

### 1. Clone and Install

```bash
cd ~ && git clone --depth 1 https://github.com/diegosouzapw/OmniRoute.git
cd OmniRoute && npm install
```

### 2. Fix Known Migration Collisions

OmniRoute v3.8.50 ships two pairs of migration files with the same numeric prefixes, both of which will crash on startup:

**Version 135 collision:**
- `135_auto_restart_adopted.sql`
- `135_migrate_model_capability_max_token.sql`

**Version 136 collision:**
- `136_dario_fallback_backend.sql`
- `136_radar_cache_settings.sql`

Error message format:
```
Migration version collision detected: version=135 → [135_auto_restart_adopted, 135_migrate_model_capability_max_token]; version=136 → [136_dario_fallback_backend, 136_radar_cache_settings].
```

Note: The collision check uses filenames **without** the `.sql` extension.

**File:** `src/lib/db/migrationRunner/constants.ts`

⚠️ **CRITICAL GOTCHA (verified 2026-08-06):** list `name`/`supersededByName` **WITHOUT** the `.sql` extension. The runner's regex (`/^(\d+)_(.+)\.sql$/`) stores the bare name, so entries carrying `.sql` never match and the server STILL crashes with the identical collision error. If the error persists after editing, suspect trailing extensions first.

Add both to the `SUPERSEDED_DUPLICATE_MIGRATIONS` array:

```ts
export const SUPERSEDED_DUPLICATE_MIGRATIONS = [
  {
    version: "041",
    name: "session_account_affinity",
    supersededByVersion: "050",
    supersededByName: "session_account_affinity",
  },
  {
    // NOTE: names here must NOT include ".sql" — see gotcha above
    version: "135",
    name: "auto_restart_adopted",
    supersededByVersion: "135",
    supersededByName: "migrate_model_capability_max_token",
  },
  {
    version: "136",
    name: "dario_fallback_backend",
    supersededByVersion: "136",
    supersededByName: "radar_cache_settings",
  },
] as const;
```

See `references/omniroute-migration-fix.md` for the exact diff and context.

### 3. Install Missing Native Dependency

OmniRoute's DB layer requires `better-sqlite3`. If `npm install` doesn't pull it in automatically:

```bash
cd OmniRoute && npm install better-sqlite3
npm rebuild better-sqlite3  # may fail on Node < 24; verify with node -e "require('better-sqlite3')"
```

### 4. Configure .env

`npm install` auto-generates `.env` from `.env.example` with auto-generated `JWT_SECRET` and `API_KEY_SECRET`. Before first run:

- Change `INITIAL_PASSWORD` from `CHANGEME` to a strong password
- Set `PORT=20128` (default)
- Add provider API keys as needed (OpenRouter, OpenAI, Anthropic, etc.)

### 5. Start Dev Server

```bash
cd OmniRoute && npm run dev
```

Dashboard: http://localhost:20128
MCP endpoint: http://localhost:20128/api/mcp/stream

### 6. Hermes MCP Integration

Add OmniRoute as an MCP server in Hermes config:

```
claude mcp add-server omniroute --type http --url http://localhost:20128/api/mcp/stream
```

This gives Claude Code (and other Hermes-managed agents) access to OmniRoute's full toolset: routing, provider management, combos, cache, compression, and memory.

### 7. Persistent Service (systemd user service)

Create `~/.config/systemd/user/omniroute.service` using the template at `templates/omniroute.service`:

```ini
[Unit]
Description=OmniRoute AI Routing Gateway
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/%u/OmniRoute
ExecStart=/home/%u/.local/bin/node --max-old-space-size=8192 scripts/dev/run-next.mjs start
Restart=on-failure
RestartSec=5
EnvironmentFile=/home/%u/OmniRoute/.env
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
```

Then:
```bash
systemctl --user daemon-reload
systemctl --user enable --now omniroute
```

See `templates/omniroute.service` for the ready-to-install unit file.

## Common Pitfalls

- **Migration collision crash**: Two files with the same numeric prefix in `src/lib/db/migrations/` will crash on startup. Check `SUPERSEDED_DUPLICATE_MIGRATIONS` in `constants.ts` and add the superseded file. Names WITHOUT `.sql` (see gotcha above).
- **"Too many pending migrations" safety abort** (after fixing collisions): fresh `~/.omniroute` DB starts at an old schema version, so 100+ pending migrations trip `MigrationSafetyAbortError`. For first boot run `OMNIROUTE_MAX_PENDING_MIGRATIONS=0 npm run dev`; later set it persistently in `.env`. If instead a STALE old DB exists (`~/.omniroute` from a previous install), deleting that directory resolves it (user approval required — recursive delete).
- **"Another next dev server is already running"**: an orphaned dev server holds the port lock. The error prints the PID — `kill <pid>` then relaunch.
- **better-sqlite3 not found**: The `npm install` may not build native bindings. Run `npm rebuild better-sqlite3` and verify with `node -e "require('better-sqlite3')"`.
- **Port already in use**: Default is 20128. Change `PORT` in `.env` if needed.
- **Node version**: Requires Node >= 22. OmniRoute uses Next.js 16 and tsx.

## Verification

After starting the dev server:
1. `curl -s -o /dev/null -w "%{http_code}" http://localhost:20128/` should return `200` or `307`
2. **No `/health` route exists** — `/health` serves an HTML 404 page even on a healthy server. Don't use it as a liveness probe.
3. `curl -s http://localhost:20128/api/health` → `{"error":{"code":"AUTH_001","message":"Authentication required"}}` means server is UP and auth-gated (this is success for an unauthenticated probe).
4. `curl -s http://localhost:20128/api/mcp/stream` → same AUTH_001 JSON = endpoint alive.
5. Dashboard at http://localhost:20128 should be accessible with the admin password set in `.env`

**Quick verification script:** `scripts/verify-omniroute.sh`

```bash
chmod +x scripts/verify-omniroute.sh
./scripts/verify-omniroute.sh
```

## Key Files

- `src/lib/db/migrationRunner/constants.ts` — migration collision overrides
- `src/lib/db/migrationRunner.ts` — migration runner logic
- `.env` — runtime configuration (auto-generated)
- `README.md` — full documentation
- `docs/ENVIRONMENT.md` — all environment variables reference
