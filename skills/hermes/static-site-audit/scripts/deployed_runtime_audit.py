"""Runtime audit of a deployed JS-framework site: what curl can't see.
Usage: python3 deployed_runtime_audit.py https://site.example [form_path]
Checks after real hydration: form fields, stat counters, animation markers,
reduced-motion support, OG/social tags, console errors.
Writes report next to itself; terminal output is a one-line status only."""
import json, os, sys
from playwright.sync_api import sync_playwright

BASE = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "https://example.com"
FORM_PATH = sys.argv[2] if len(sys.argv) > 2 else "/contact"
UA = "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "runtime_audit_report.txt")

lines = [f"=== RUNTIME AUDIT {BASE} ==="]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=["--lang=en-US"])
    ctx = browser.new_context(user_agent=UA, viewport={"width": 1440, "height": 900})
    errors = []
    pg = ctx.new_page()
    pg.on("console", lambda m: errors.append(f"{m.type}: {m.text[:150]}") if m.type == "error" else None)
    pg.on("pageerror", lambda e: errors.append(f"pageerror: {str(e)[:180]}"))

    # --- forms after hydration ---
    pg.goto(f"{BASE}{FORM_PATH}", wait_until="networkidle", timeout=60000)
    pg.wait_for_timeout(2500)
    fields = pg.evaluate("""() =>
      Array.from(document.querySelectorAll('input, textarea, select')).map(el => ({
        tag: el.tagName.toLowerCase(), type: el.type || '', name: el.name || '', required: el.required}))
    """)
    lines += ["", f"--- {FORM_PATH} after JS ---", f"fields: {json.dumps(fields)}"]
    if not fields:
        lines.append("!! NO FORM FIELDS RENDERED — check client-side-only rendering or wrong path")

    # --- home page runtime ---
    pg.goto(BASE, wait_until="networkidle", timeout=60000)
    pg.wait_for_timeout(3000)
    res = pg.evaluate("""() => {
      const numEls = () => Array.from(document.querySelectorAll('*'))
        .filter(el => /^\\d+\\+?$/.test(el.textContent.trim()) && el.children.length === 0).length;
      return {
        h1: document.querySelector('h1')?.textContent.trim().slice(0, 90) || null,
        svg_long_paths: Array.from(document.querySelectorAll('svg path')).filter(p => (p.getAttribute('d')||'').length > 200).length,
        counter_candidates_before_scroll: numEls(),
        keyframes_in_style: Array.from(document.querySelectorAll('style')).some(s => s.textContent.includes('@keyframes')),
        reduced_motion_css: Array.from(document.querySelectorAll('style')).some(s => s.textContent.includes('prefers-reduced-motion')),
        og_title: !!document.querySelector('meta[property="og:title"]'),
        og_image: !!document.querySelector('meta[property="og:image"]'),
        twitter_card: !!document.querySelector('meta[name="twitter:card"]'),
        canonical: !!document.querySelector('link[rel="canonical"]'),
        json_ld: document.querySelectorAll('script[type="application/ld+json"]').length,
      };
    }""")
    lines += ["", "--- / runtime ---"] + [f"{k}: {v}" for k, v in res.items()]

    for _ in range(6):
        pg.mouse.wheel(0, 800)
        pg.wait_for_timeout(400)
    counters_after = pg.evaluate("""() =>
      Array.from(document.querySelectorAll('*'))
        .filter(el => /^\\d+\\+?$/.test(el.textContent.trim()) && el.children.length === 0)
        .map(e => e.textContent.trim())""")
    lines.append(f"stat numbers visible after scroll: {counters_after}")

    seo = pg.evaluate("""() => fetch(window.location.origin + '/robots.txt')
      .then(r => r.text()).then(t => t.slice(0, 300)).catch(() => 'FETCH FAILED')""")
    lines += ["", "--- robots.txt ---", str(seo)]

    lines += ["", f"console errors ({len(errors)}):"] + ([f"  {e}" for e in errors[:12]] or ["  none"])
    browser.close()

with open(OUT, "w") as f:
    f.write("\n".join(lines))
print(f"report -> {OUT}")
