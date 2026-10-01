"""Single-site full-content recovery scraper.
Produces: pages/*.md + posts/*.md (front matter + markdown), raw_html/*.html,
media/*, manifest.json. Edit URLS + BASE + selectors, then run.

Usage: python3 site_recovery_scraper.py
"""
import json, os, re, time, urllib.parse
from datetime import datetime

import requests
from bs4 import BeautifulSoup
import html2text

# ---------- EDIT ME ----------
BASE = "https://www.example.com"
URLS = [  # (url, kind)  kind: page | post
    ("https://www.example.com/", "page"),
]
# --------------------------

OUT = os.path.expanduser("~/site_recovery")
RAW_DIR = os.path.join(OUT, "raw_html")
MD_PAGES = os.path.join(OUT, "pages")
MD_POSTS = os.path.join(OUT, "posts")
MEDIA_DIR = os.path.join(OUT, "media")
for d in (RAW_DIR, MEDIA_DIR):
    os.makedirs(d, exist_ok=True)
os.makedirs(MD_PAGES, exist_ok=True)
os.makedirs(MD_POSTS, exist_ok=True)

UA = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}
# Some shared-host servers (LiteSpeed/Apache) reject python-urllib with 406
# while accepting curl with the same headers. Fall back to curl subprocess on 406.
CURL_FALLBACK = ["curl", "-sL", "--max-time", "40",
                 "-H", "User-Agent: " + UA["User-Agent"],
                 "-H", "Accept: " + UA["Accept"]]
LOG = []

def log(m):
    print(m, flush=True)
    LOG.append(str(m))

h2t = html2text.HTML2Text()
h2t.body_width = 0

CONTENT_SELECTORS = ["div.entry-content", "article", "main", "#content",
                     "div.site-content", "#main", "body"]


def fetch(url, tries=4):
    """GET with parse-validation; retries transient junk bodies.
    Falls back to curl subprocess on HTTP 406 (some shared hosts reject
    python-urllib's User-Agent while accepting curl with the same headers)."""
    import subprocess
    last = None
    for a in range(tries):
        try:
            r = requests.get(url, headers=UA, timeout=40)
            r.raise_for_status()
            if len(r.text) > 3000 and "<html" in r.text.lower():
                return r.text
            last = RuntimeError(f"suspicious body len={len(r.text)}")
        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == 406:
                # Server rejects python's User-Agent. Try curl directly.
                try:
                    out = subprocess.run(
                        CURL_FALLBACK + [url], capture_output=True, timeout=40
                    )
                    if out.returncode == 0 and len(out.stdout) > 3000:
                        return out.stdout.decode("utf-8", errors="replace")
                except Exception as ce:
                    last = ce
            else:
                last = e
                time.sleep(2 * (a + 1))
        except Exception as e:
            last = e
            time.sleep(2 * (a + 1))
    raise RuntimeError(f"fetch failed {url}: {last}")


def extract_content(soup):
    for sel in CONTENT_SELECTORS:
        node = soup.select_one(sel)
        if node and len(node.get_text(strip=True)) > 200:
            return node
    return soup.body or soup


def safe_name(url):
    p = urllib.parse.urlparse(url).path
    return re.sub(r"[^A-Za-z0-9._-]", "_", os.path.basename(p) or "file")[-100:]


def local_images(node, page_url, page_slug, downloaded):
    """Download imgs, rewrite src to local relative path.
    Uses page_url (not BASE) as the join base so relative paths like
    '../assets/img/1.jpg' resolve correctly when the page lives in a
    subdirectory (e.g. /cbse/cbse_faculty.html)."""
    out_urls = []
    for img in node.find_all("img"):
        src = img.get("src") or img.get("data-src")
        if not src:
            continue
        # Anchor the join to the page's own URL, not the site root
        absu = urllib.parse.urljoin(page_url, src)
        if not absu.startswith("http"):
            continue
        name = safe_name(absu)
        if not re.search(r"\.(jpg|jpeg|png|gif|webp|svg)$", name, re.I):
            name += ".jpg"
        prefix = f"{page_slug[:30]}_" if name in downloaded else ""
        fname = prefix + name
        dest = os.path.join(MEDIA_DIR, fname)
        if fname not in downloaded and absu not in downloaded.values():
            try:
                ir = requests.get(absu, headers=UA, timeout=60)
                ir.raise_for_status()
                with open(dest, "wb") as f:
                    f.write(ir.content)
                log(f"    img {fname} ({len(ir.content)//1024} KB)")
                downloaded[fname] = absu
            except Exception as e:
                log(f"    img FAIL {absu}: {e}")
                continue
        elif absu in downloaded.values():
            fname = [k for k, v in downloaded.items() if v == absu][0]
        img["src"] = f"media/{fname}"
        if img.get("srcset"):
            del img["srcset"]
        out_urls.append({"file": fname, "url": absu, "alt": img.get("alt", "")})
    return out_urls


def slug_from(url):
    p = urllib.parse.urlparse(url).path.strip("/")
    return re.sub(r"[^a-z0-9]+", "-", p.lower()).strip("-")[:80] or "home"


manifest = {"base": BASE, "scraped_at": datetime.now().isoformat(timespec="seconds"),
            "pages": []}
downloaded = {}

for url, kind in URLS:
    slug = slug_from(url)
    log(f"[{kind}] {url}")
    html = fetch(url)
    with open(os.path.join(RAW_DIR, f"{slug}.html"), "w") as f:
        f.write(html)

    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.get_text(strip=True) if soup.title else slug
    md_tag = soup.find("meta", attrs={"name": "description"})
    meta_desc = md_tag.get("content", "") if md_tag else ""

    content = extract_content(soup)
    images = local_images(content, url, slug, downloaded)

    navs = []
    for nav in soup.select("nav ul li a, .menu-item a")[:60]:
        t, h = nav.get_text(strip=True), nav.get("href", "")
        if t and h and {"title": t, "href": h} not in navs:
            navs.append({"title": t, "href": h})

    inner = content.decode_contents() if hasattr(content, "decode_contents") else str(content)
    markdown = h2t.handle(inner)
    front = ["---", f"url: {url}", f"slug: {slug}", f"type: {kind}", f"title: {title}"]
    if meta_desc:
        front.append(f"meta_description: {meta_desc}")
    front.append("---")

    md_path = MD_PAGES if kind == "page" else MD_POSTS
    with open(os.path.join(md_path, f"{slug}.md"), "w") as f:
        f.write("\n".join(front) + f"\n\n# {title}\n\n" + markdown)

    manifest["pages"].append({
        "url": url, "slug": slug, "type": kind, "title": title,
        "meta_description": meta_desc, "images": images,
        "navigation_links": navs,
        "html_bytes": len(html), "md_chars": len(markdown),
    })
    log(f"    saved: {title[:50]!r} imgs={len(images)} md={len(markdown)}ch")
    time.sleep(1.2)

with open(os.path.join(OUT, "manifest.json"), "w") as f:
    json.dump(manifest, f, indent=2)
with open(os.path.join(OUT, "extract.log"), "w") as f:
    f.write("\n".join(LOG))
print(f"\nDONE: {len(manifest['pages'])} pages -> {OUT}")
print("Next: scan raw_html/ for external-domain image hotlinks (likely dead); "
      "write REBUILD_BRIEF.md per the skill.")
