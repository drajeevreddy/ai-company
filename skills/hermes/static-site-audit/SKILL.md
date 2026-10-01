---
name: static-site-audit
description: Use when auditing a site for errors/broken links — local static projects OR deployed URLs (Vercel/Next.js) the user wants reviewed.
---

# Static Site Audit

Audit a static website's integrity: broken internal links, missing assets, invalid JSON, security defaults, version-control status. Produces a severity-ranked report with actionable fixes.

## When to use
- User asks to "check the site for errors", "find broken links", "pull status off my project", "is anything going on with the site"
- Before/after deploys of a static HTML/PHP project
- Routine site health checks (recurring for site owners)
- User shares a **deployed URL** (Vercel/Netlify/prod) and asks "is anything missing / review my build"

## Workflow

1. **Locate the project.** Check `~/` for likely folders; use session_search for context on what the user calls "the project". Check modification times (`find . -type f -newermt "YYYY-MM-DD 00:00"`) to see what changed recently.
2. **Run the link checker**: `python3 scripts/check_links.py <root>` (server-aware; see below).
3. **Parallel integrity checks**:
   - JSON validity: walk `*.json`, `json.load` each.
   - PHP lint: `php -l` **only if the `php` binary exists** — otherwise skip silently, never report the missing binary as a site error.
   - Security scan: look for shipped `admin.json`, default `password_hash(...)` calls, hardcoded creds (`Admin@123`-style defaults auto-created on first run).
   - Git status: note if the project is not under version control.
   - Look for staging copies (`*_upload`, `dist`, `backup*` dirs) — determine which copy is the real deploy target before reporting a broken copy as a live-site error.
4. **Report**: group findings by real-vs-false-positive, severity (🔴 broken links / 🟠 security or single broken link / 🟡 fragility), with the affected file and the fix. Offer to fix, don't just list.

## Critical: server-aware link resolution (avoid false positives)

Naive `href`/`src` extraction on a site with **clean URLs / Apache MultiViews / extensionless links** reports hundreds of false "missing" targets — `href="doctors"` is fine when `doctors.html` exists. Resolution rules (all in `scripts/check_links.py`):

- Extensionless basename → try `+ .html`, `+ .php`.
- Directory path → try `index.html`, `index.php`.
- URL-decode (`%20` → space), strip `?query` and `#hash` before checking.
- Skip absolute/scheme refs (`/`, `http:`, `mailto:`, `tel:`, `data:`, `javascript:`, `//`) — can't verify locally.
- Resolve `../`-relative refs **from each file's own directory** and check the resolved path — catches wrong-depth links (e.g. `../../../endocrine-atlas.html` from a nested `topics/x.html` resolving outside the site root).
- Count and group by resolved target so one systemic bug (every page in a folder uses one wrong depth) shows as one issue, not a thousand.

## Pitfalls
- Override-stylesheet scoping (learned restyling a 25-page site): a broad
  selector like `.nav-links a` also hits dropdown/mega-menu card anchors —
  scope to top-level with `.nav-links > li > a`. Never put global
  `h1,h2,h3`, `.btn`, or bare `a:hover` rules in a nav-theme override.
  Prefer `position: sticky` for the restyled bar — `fixed` overlaps
  inner-page heroes that lack the homepage's top padding. See
  `references/restyle-debugging-recipes.md`.
- Invisible content that IS in the DOM: `opacity: 0` animation classes
  (`.fade-in-up`) whose `visible` class is added by an IntersectionObserver
  watching a DIFFERENT selector (`.fade-up`) stay hidden forever. When a
  section looks like an empty gap, check observer-selector coverage before
  touching layout.
- `background: transparent !important` on hero classes silently kills
  inline-style hero background images on every page that sets one.
- Pages opened via `file://` load zero CDN assets if the browser blocks
  external requests → blank icon tiles + fallback fonts. Self-host
  Font Awesome + Google Fonts (latin subset via the css2 API) inside the
  project; verify with grep that no `cdnjs`/`googleapis` refs remain.
- `php: command not found` → just skip linting and do a static scan; never report it as a site error.
- Folders with spaces in names (`dr mahesh book/`) produce `%20` links that work but are fragile — recommend renaming, note that links must be rewritten together.
- A shipped `admin.json` with default credentials is a security issue even if `.htaccess` blocks web access — flag it and tell the user to change it.
- Not under git = high risk for a large static site; recommend `git init` + first commit before further uploads.
- Revert scope: after multi-area work, a bare "revert" is ambiguous — a full restore destroys good fixes along with bad ones. Confirm scope in one short question ("everything, or just X?") before touching anything. Keep a pristine baseline (zip copy or snapshot dir) so any revert is surgical: `diff -rq baseline dir` gives the exact footprint, restore only those paths, then re-verify with a second diff (expect clean).

## Auditing a DEPLOYED JS-framework site (Vercel/Next.js/etc.)

Static HTML tells you almost nothing about a hydrated app: forms, counters and
animations render client-side only. When the user shares a deployed URL:

1. **curl pass** (cheap first): status codes for every route in the nav/sitemap,
   `<title>`, meta description presence, `sitemap.xml`/`robots.txt` validity,
   content markers (names, phones) — but treat "missing" as *unconfirmed*, not broken.
2. **Playwright pass** — run `python3 scripts/deployed_runtime_audit.py <url> [form_path]`.
   It checks after real hydration: form fields + required flags, stat counters
   before/after scroll, SVG animation paths, keyframes, reduced-motion support,
   OG/twitter/canonical tags, JSON-LD count, console errors.
3. Known failure shapes to check by name: OG/social tags absent (breaks WhatsApp/
   LinkedIn share cards), sitemap/robots referencing the OLD domain instead of the
   deploy domain, no `prefers-reduced-motion` handling despite animated UI.
4. Report what curl CAN'T see separately from what's genuinely missing — "form
   renders zero fields in static HTML" is usually fine; verify in the browser pass.

## Safe bulk re-theme / bulk-edit without breaking links

When the user wants a visual restyle (new nav, theme, fonts) across many
static pages with a hard constraint like "don't change any links":

1. **Snapshot first**: `python3 scripts/href_snapshot.py snapshot <root> -o /tmp/refs_before.json`.
2. **Additive override only** — create NEW files (e.g. `brand-theme.css`,
   `brand-nav.js`) and inject only `<link>`/`<script>` tags. Never edit
existing markup, hrefs, or menu items. One override file beats patching a
160KB shared stylesheet; nested pages get the same files with adjusted
relative paths (`../brand-theme.css`).
3. **Diff after**: `python3 scripts/href_snapshot.py diff /tmp/refs_before.json <root>` —
   every pre-existing ref must still be present (exit 1 otherwise).
4. **Live-verify**: serve locally (`python3 -m http.server`), load in the
browser, and eval one computed-style expression (nav position, link
font-size/letter-spacing/transform, brand color, injected-node count) —
DOM truth beats eyeballing when screenshots are unavailable. Scope
functional sub-apps (PHP tools, calculators) OUT unless asked; say so.

## Support files
- `scripts/href_snapshot.py` — snapshot/diff all href+src refs across *.html before/after bulk edits; proves no link changed.
- `scripts/deployed_runtime_audit.py` — Playwright runtime audit of deployed JS sites; writes a report file (never trust terminal echo for verification detail).
- `references/shashi-advanced-health-site.md` — site map + known issues for the Shashi Advanced Health project (recurring audit target).
