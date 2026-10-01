---
name: site-content-recovery
description: "Use when a site must be fully scraped for a rebuild."
version: 1.0.0
category: software-development
---

# Site Content Recovery

Capture everything of value from an existing live website — text, structure,
media, metadata — into an organized local archive that a rebuild can consume,
when the original CMS/database/dev access is gone.

## When to Use

- User's own site is being rebuilt; ex-dev "ran away"; no repo/hosting access.
- Site migrations, pre-shutdown archiving, "copy my old site's content".
- Distinct from web-scraping-pipelines (that = many records into a spreadsheet;
  this = one site, everything, faithful archive).

## Workflow

### Option A: Full Scrape (original workflow)
1. **Probe before scraping.** `curl` the homepage: read `<title>`,
   `name="generator"` meta (WordPress/Shopify/etc.), robots.txt, sitemap.xml.
   WordPress: check `/wp-json/wp/v2/pages?per_page=1&_fields=id` — if it returns
   valid JSON you get counts (`X-WP-Total` header), slugs, clean HTML bodies.
2. **Validate every API/HTTP body — never trust status 200.** Some stacks
   (LiteSpeed cache in front of WordPress) intermittently return HTTP 200 +
   `application/json` content-type with a CORRUPTED body — plain page text or
   truncated JSON. Parse-check every response; retry with backoff; if a specific
   URL pattern keeps failing while others pass, that URL is poisoned in cache
   (cache-busting params do NOT help) and you must switch strategies.
3. **Fallback that always works: sitemap-driven rendered-HTML scrape.**
   Pull all `<loc>` URLs from the sitemap(s), fetch each rendered page, extract
   the content node via selector cascade
   (`div.entry-content → article → main → #content → body`),
   convert to Markdown, AND save the raw HTML alongside.
4. **Archive shape (deliver exactly this):**
   - `pages/*.md`, `posts/*.md` — YAML-ish front matter (url, slug, title, meta
     description) + converted content
   - `raw_html/*.html` — fidelity reference
   - `media/` — downloaded images, names rewritten to local relative paths in
     the markdown
   - `manifest.json` — per-page title/meta/images/nav links/byte sizes
   - `REBUILD_BRIEF.md` — human handoff: nav structure, page inventory, media
     inventory incl. what is lost and why, functional notes (form plugins etc.)
5. **Media:** download every self-hosted asset referenced anywhere in the raw
   HTML (not just inside the content node — headers/sliders/footer count).
   For hotlinked external images see references/wayback-image-rescue.md.
6. **Finish with functional notes:** identify form plugin (CF7 shortcodes /
   markup), sliders, embeds — these are the rebuild requirements users forget.

### Option B: Local Template Migration (when you have source files + target UI)
Use when the old site's PHP/HTML files are available locally AND you have a
new UI template (single HTML file or similar) to migrate into.

1. **Inventory source files.** List all `.php`/`.html` pages, extract:
   - Page metadata (title, description, keywords from PHP variables or `<meta>`)
   - Content blocks (hero, services, portfolio items, team, testimonials, FAQ)
   - Structured data (portfolio URLs, images, categories, event dates)
   - Contact info, footer links, social links
   - Media assets (copy entire `images/` folder)
2. **Anchor-based replacement on target template.** Load the new UI HTML as a
   string; for each content piece, find a unique anchor in the target (e.g.
   `WE MAKE` in hero, `TREND-AWARE` in values) and replace with source content.
   Use assertions to catch missing anchors — fail fast if template changed.
3. **Data-driven sections.** For repeatable blocks (services grid, portfolio,
   events/blog), build JS data objects in the template (`const SERVICES = []`,
   `const PROJECTS = {}`) and replace the entire array literal via regex with
   a callback (avoids escaping issues).
4. **Theme/behavior cleanup.** Remove unwanted features (dark-mode toggle,
   custom cursor, theme boot script) by deleting their HTML, CSS blocks, and
   JS sections entirely — don't just hide them.
5. **Responsive cleanup.** Remove staggered layout helpers (e.g.
   `margin-top` on nth-child) when grid `gap:0` makes them unnecessary.
6. **Verify in browser.** Spin up local server (`python3 -m http.server`),
   check: no `data-theme` attributes remain, all images load (200), no
   console errors, footer year/current, phone numbers correct.
7. **Deliver:** migrated `index.html` + `images/` + any standalone pages
   (privacy/terms) with matching theme.

## Pitfalls

- **Hotlinked images are the #1 data loss in abandoned sites.** Scan raw HTML
  for `src=` on other domains; expect DNS failures. Attempt Wayback rescue
  (see reference), then report losses explicitly with replacement suggestions.
- **WordPress REST API corruption is intermittent, not constant** — small
  requests may parse fine while `per_page=100` URLs fail consistently. Don't
  conclude "API broken" or "API fine" from one probe; test the exact patterns
  you'll hammer, then prefer the HTML path if any doubt.
- **Download failures get noisy:** log each media file with its size so the
  final report distinguishes 0-byte failures from real saves.
- Politeness: 1–2 s between page fetches is plenty for a small site; a
  30-page capture takes under a minute.
- **Python's `urllib`/`requests` User-Agent gets 406 from servers that accept
  curl with a real browser UA.** Some shared-host Apache configs (seen on
  school sites, LiteSpeed, CDNs with strict bot rules) accept `curl` with
  `User-Agent: Mozilla/5.0 ... Chrome/120.0 Safari/537.36` + `Accept: text/html`
  but reject Python's default `python-urllib/3.x` with HTTP 406 Not Acceptable.
  Symptom: `curl` works, the Python script fails on the same URL. Fix: use a
  full browser-style UA AND `Accept`/`Accept-Language` headers; if `requests`
  still gets 406, fall back to `subprocess.run(["curl", ...])` for stubborn URLs.
  The two errors look the same to the script but the curl UA is what the server
  is actually filtering on.
- **504 / 502 / SSL-handshake-timeout ≠ 404.** When parallel-fetching 50+ URLs
  from one host, transient 504s and SSL timeouts are the server rate-limiting
  the burst, not the page being missing. Retry those URLs with `time.sleep(2-3)`
  between attempts; a real 404 stays a 404 across 3 retries. A real page either
  returns 200 with a non-trivial body (heuristic: >2 KB and contains `<html`)
  OR it returns a real 404. Do not lump them into one "failed" bucket.
- **Nested paths collide when you flatten URLs to filenames.** A site with
  `cbse/index.html` and `cbse/cbse_xxx.html` flattens to `cbse_index.html`
  and `cbse_cbse_xxx.html` only if your path-stripping rule is `replace("/", "_")`.
  It breaks for paths where the section name and the page slug share a prefix
  (e.g. `/stateboard/state_faculty.html` → `stateboard_state_faculty.html`, fine;
  but `/stateboard/contact.html` and `/cbse/contact.html` both want
  `stateboard_contact.html` and `cbse_contact.html`, also fine — the rule is
  "use the full path after BASE" not "use the last segment"). The earlier
  pattern of `url.split('/')[-1]` collides as soon as two sections share a
  filename like `contact.html`. Always include the parent directory in the
  filename.
- **Some sites have relative image URLs that need `urljoin(per-page, src)`,
  not `urljoin(BASE, src)`.** If `cbse/cbse_faculty.html` has
  `src="../assets/img/team/1.jpg"`, the BASE-anchored join gives a broken
  path. Track the per-page URL and join against that, not the site root.

## Parallel download recipe (50+ pages, 100+ images)

For sites with more than ~20 pages, sequential is too slow. Use
`concurrent.futures.ThreadPoolExecutor` with `max_workers=10-15`:

```python
def fetch(url, fn):
    try:
        with urllib.request.urlopen(req_with_browser_ua(url), timeout=15) as r:
            Path(fn).write_bytes(r.read())
        return (url, "ok", len(Path(fn).stat().st_size))
    except HTTPError as e:
        return (url, f"http_{e.code}", 0)
    except Exception as e:
        return (url, f"err_{type(e).__name__}", 0)
```

After the burst, bucket the failures: `http_404` is a real missing page (record
+ skip), `http_406/504/502` and `ssl_handshake_timeout` are transient (retry
sequentially with `sleep(2)` between, then fall back to `subprocess.run(["curl", ...])`
if the second retry also 406s). At the end you should have a clean
`ok / 404 / transient_failed` partition — never mix 404s with transient errors
in the "missing" report.

For images: same pattern, but resolve to absolute URLs first using the
per-page URL as the join base, and store them in a section-aware directory
(`/images/cbse/1.jpg` not `/images/1.jpg`) so duplicates across sections don't
overwrite each other.

## Support Files

- templates/site_recovery_scraper.py — working single-site scraper producing
  the full archive shape above; edit URLS/selectors and run.
- references/wayback-image-rescue.md — escalating recipe for recovering
  dead-hotlinked images from the Internet Archive, incl. when they are
  provably lost.
