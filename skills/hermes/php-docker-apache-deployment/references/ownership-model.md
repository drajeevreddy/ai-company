# Ownership Model: Why 1000:1000 + chmod 777 Works

## The Conflict
| Entity | User | UID | Needs |
|--------|------|-----|-------|
| Host user | painarise | 1000 | `git pull`, `git commit`, edit tracked files |
| Container Apache | www-data | 33 | Write to `data/`, `config/`, `logs/`, `uploads/` |

## Failed Approach: `chown www-data:www-data`
```bash
chown -R www-data:www-data /var/www/html
```
**Result**: Host user (1000) can no longer `git pull` — files owned by 33, no write permission.

## Working Approach: Dual Permissive Model

### Step 1: Tracked Files → Host Owner (1000:1000)
```bash
docker exec appointment chown -R 1000:1000 /var/www/html
```
- All PHP, CSS, JS, HTML files writable by host user
- `git` operations work normally
- Container Apache can **read** (world-readable 644)

### Step 2: Runtime Directories → World-Writable (777)
```bash
chmod -R 777 data config logs uploads
```
- `www-data` (33) can write CSV, logs, uploads
- Host user (1000) can also write/clean
- `.htaccess` in each dir still blocks web access to sensitive files

## Why 777 Is Acceptable Here
1. `.htaccess` in `data/`, `config/`, `includes/`, `logs/`, `uploads/` denies all web access
2. These dirs are not served as static content — only PHP includes/reads them
3. Host is single-user dev box; no untrusted local users
4. Container is isolated; only Apache inside accesses these paths

## Alternative: ACLs (More Precise, More Complex)
```bash
setfacl -R -m u:33:rwx -m u:1000:rwx data config logs uploads
setfacl -R -d -m u:33:rwx -m u:1000:rwx data config logs uploads
```
Works but requires `acl` package and is harder to explain. 777 + `.htaccess` is simpler and equally secure for this threat model.

## Git Cleanliness
Before commit:
```bash
git checkout -q -- data logs uploads
```
Discards any local CSV data changes so only code changes are committed.