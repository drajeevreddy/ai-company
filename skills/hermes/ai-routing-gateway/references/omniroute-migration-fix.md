# OmniRoute Migration Collision Fix

## Problem

OmniRoute v3.8.50 ships **two pairs** of migration files with the same numeric prefixes, both of which will crash on startup:

### Version 135 collision
- `135_auto_restart_adopted.sql`
- `135_migrate_model_capability_max_token.sql`

### Version 136 collision
- `136_dario_fallback_backend.sql`
- `136_radar_cache_settings.sql`

The migration runner detects these as collisions and crashes on startup with:

```
Migration version collision detected: version=135 → [135_auto_restart_adopted, 135_migrate_model_capability_max_token]; version=136 → [136_dario_fallback_backend, 136_radar_cache_settings].
Each migration file must have a unique numeric prefix. Rename one of the files
(and add a retroactive guard in isSchemaAlreadyApplied for DBs that already
applied the old number).
```

Note: The collision check uses filenames **without** the `.sql` extension (e.g., `135_auto_restart_adopted` vs `135_migrate_model_capability_max_token`).

## Fix

Add both superseded files to `SUPERSEDED_DUPLICATE_MIGRATIONS` in `src/lib/db/migrationRunner/constants.ts`.

### Before

```ts
export const SUPERSEDED_DUPLICATE_MIGRATIONS = [
  {
    version: "041",
    name: "session_account_affinity",
    supersededByVersion: "050",
    supersededByName: "session_account_affinity",
  },
] as const;
```

### After

⚠️ Names must be listed **without** the `.sql` extension (verified live 2026-08-06: an earlier revision of this doc showed `.sql` names and the server still crashed with the identical error until they were stripped):

```ts
export const SUPERSEDED_DUPLICATE_MIGRATIONS = [
  {
    version: "041",
    name: "session_account_affinity",
    supersededByVersion: "050",
    supersededByName: "session_account_affinity",
  },
  {
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

## How It Works

The migration runner in `src/lib/db/migrationRunner.ts` (lines 238-268) groups migration files by numeric prefix. If more than one file shares a prefix, it checks `SUPERSEDED_DUPLICATE_MIGRATIONS` to see if the collision is a known rename. If the file is listed there, it is excluded from the collision check and the other file wins.

## Verification

After applying the fix, start the dev server:

```bash
cd OmniRoute && npm run dev
```

The server should start without the migration collision error. Verify with:

```bash
curl -s -o /dev/null -w "%{http_code}" http://localhost:20128/
# Expected: 200
```