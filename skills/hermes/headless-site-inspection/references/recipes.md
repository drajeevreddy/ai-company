# Validated Recipes (session 2026-08-22)

## 1. Instagram follower counts, no login (25/25 hit rate)

Search-snippet route only hits ~24% (6/25). Direct profile og:description hits 100%.

```python
import re, time, json
from playwright.sync_api import sync_playwright

def num(s):
    s = s.replace(",", "").strip().upper()
    m = re.match(r'([\d.]+)([KM]?)', s)
    return int(float(m.group(1)) * {"K": 1e3, "M": 1e6}.get(m.group(2), 1)) if m else None

PAT = re.compile(r'([\d,.]+[KM]?)\s*Followers,\s*([\d,.]+[KM]?)\s*Following,\s*([\d,.]+[KM]?)\s*Posts', re.I)

def scrape(handles):
    found = {}
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
        ctx = b.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131 Safari/537.36")
        pg = ctx.new_page()
        for h in handles:
            try:
                pg.goto(f"https://www.instagram.com/{h}/", timeout=25000, wait_until="domcontentloaded")
                pg.wait_for_timeout(3500)
                desc = pg.locator('meta[property="og:description"]').get_attribute("content") or ""
                m = PAT.search(desc)
                if m:
                    found[h] = {"followers": num(m.group(1)), "following": num(m.group(2)), "posts": num(m.group(3))}
            except Exception as e:
                print(h, "ERR", str(e)[:60])
            time.sleep(2.2)   # politeness + rate-limit avoidance
        b.close()
    return found
```

Notes:
- No login needed for og:description on public profiles (as of 2026-08).
- Sleep >=2s per handle; 25 handles ran clean.
- Always label output files with source ("public IG profile metadata") + date.
- If the profile page returns a login-wall snapshot or `og:description` is missing/blank,
  do not blindly retry the same route. Treat that as platform gating, fall back to
  asking the user for screenshots/captions/top-post text, or pivot to another public
  signal source. This can happen on some accounts/pages even when the recipe usually works.

## 2. Google Drive folder listing without auth/API keys

```bash
curl -s "https://drive.google.com/embeddedfolderview?id=FOLDER_ID#list" -o drive.html
```

```python
import re
html = open('drive.html').read()
entries = re.findall(r'flip-entry" id="entry-([\w-]+)".*?href="([^"]+)".*?flip-entry-title">([^<]*)', html, re.S)
folders = [(u, n.strip()) for i, u, n in entries if '/folders/' in u]
files   = [(u, n.strip()) for i, u, n in entries if '/folders/' not in u]
```

- Names are HTML-escaped (`&amp;` for `&`) — unescape before writing to files.
- Duplicate names are common (same client multiple folders) — they are distinct entries.
- Works on folders shared "anyone with link".

## 3. Dead-domain forensics order

```bash
dig +short DOMAIN NS        # ns1.dns-expired.com => domain EXPIRED, renew at registrar
curl -s "https://web.archive.org/cdx/search/cdx?url=DOMAIN*&output=json&filter=statuscode:200"
```

- Wayback rate-limits fast (HTTP 429); sleep 5s between calls; empty result = never archived.
- Registrar parking pages return HTTP 200 with title "Your domain is expired" — check body, not status.
- Google favicon cache: `https://www.google.com/s2/favicons?domain=X&sz=256` — sometimes HTML error, check `file` output.
- SEO audit sites (simplifiedseotools.com/seo-site-audit/domain/X) cache old titles/descriptions; fetch with browser UA.

## 4. Design-token DOM extraction (single evaluate, ~400 elements)

See templates/playwright_capture.py TOKEN_JS. Key points:
- Tally computed backgroundColor/color frequencies — real palette beats guessing from CSS source.
- Grep inline `<style>` for font-family declarations; Framer/Next sites self-host woff2.
- Headlines baked as images (Framer word-art) appear in `images[]`, not `headings[]` — that's an SEO weakness worth noting in teardowns.
