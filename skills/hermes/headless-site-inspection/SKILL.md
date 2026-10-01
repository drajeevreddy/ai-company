---
name: headless-site-inspection
description: Use when scraping or visually inspecting websites from CLI.
---

# Headless Site Inspection

Class of work: visually/scrape-inspecting websites from the terminal when the interactive
browser stack is unavailable or unnecessary — design teardowns, competitor analysis,
brand-asset recovery from dead domains, social-metric harvesting.

## Core method: Python Playwright (validated)

Check availability first: `python3 -c "import playwright"` (system python often has it).
If missing, do NOT assume failure — try `pip install playwright && playwright install chromium`.

Working launch recipe (incl. WebGL sites like lusion.co):
```python
from playwright.sync_api import sync_playwright
b = p.chromium.launch(headless=True, args=["--enable-gpu","--use-gl=angle",
    "--use-angle=swiftshader","--disable-dev-shm-usage","--no-sandbox"])
ctx = b.new_context(viewport={"width":1600,"height":900}, user_agent="<real Chrome UA>")
pg.goto(url, timeout=45000, wait_until="domcontentloaded")
pg.wait_for_timeout(9000-12000)   # WebGL/animation sites need long settles
```
Pitfalls:
- WebGL canvases render black unless the swiftshader GL args above are present.
- Sites behind bot checks (Cloudflare, custom) return interstitials — detect title
  "Just a moment..." / "Not Supported" and report honestly instead of analyzing garbage.
- Screenshot timeouts on heavy sites: catch, retry once after extra wait.
- Batch independent sites through ONE browser context sequentially (new_page each).

Design-token extraction: run one `page.evaluate()` walking up to ~400 elements,
tallying `getComputedStyle().backgroundColor/color` frequencies, collecting h1/h2 text,
button labels, font-family declarations, image srcs. Full recipe in
templates/playwright_capture.py (copy + modify).

Vision pairing: feed 1–3 screenshots per vision_analyze call with pointed questions;
full-page PNG gives section-by-section structure. Save artifacts to a project
competitors/<site>/ folder alongside a DESIGN-TEARDOWN.md.

## Dead-domain / brand recovery

Order of attack (all validated 2026-08):
1. Live check + DNS: `dig +short domain NS` — nameservers like ns*.dns-expired.com
   mean the DOMAIN EXPIRED; registrar serves a parking page. Tell the user to renew.
2. Wayback: `https://web.archive.org/cdx/search/cdx?url=DOMAIN*&output=json&filter=statuscode:200`
   (rate-limits 429 easily; sleep between calls). Empty CDX = site never archived.
3. Brand marks: `https://www.google.com/s2/favicons?domain=X&sz=256` (may 404/HTML);
   SEO-audit pages (simplifiedseotools etc.) store cached titles/descriptions via plain curl.
4. Social bios carry brand info: IG og:description, FB page descriptions.

## Quick data recipes (details + snippets in references/recipes.md)

For JS-SPA shells (empty `<div id="root">` + bundle script): skip rendering,
analyze the JS bundle and probe the backend API directly — full workflow in
references/spa-bundle-scraping.md (incl. camofox server recovery).

- Google Drive folder listing WITHOUT auth/API:
  `curl https://drive.google.com/embeddedfolderview?id=FOLDER_ID#list` → parse
  `flip-entry" id="entry-<id>" ... href="URL" ... flip-entry-title">NAME`. Works for
  subfolders vs files by checking `/folders/` in href.
- Instagram follower counts (public profiles, no login): headless-load
  `instagram.com/<handle>/`, read `meta[property=og:description]`, regex
  `([\d,.]+[KM]?)\s*Followers,\s*([\d,.]+[KM]?)\s*Following,\s*([\d,.]+[KM]?)\s*Posts`.
  Sleep ~2.2s between handles; 100% hit rate vs ~24% via search snippets.
  K/M suffix decode: value * {"K":1e3,"M":1e6}.

## Reporting discipline

Real scraped numbers > estimates. Label source + date in any data file written
(e.g. results_social.json). Never fabricate private metrics (ROAS/revenue) — leave
explicit slots for the owner to fill.
