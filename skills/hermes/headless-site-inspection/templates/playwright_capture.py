#!/usr/bin/env python3
"""Copy-modify template: capture screenshots + design tokens from websites.

Usage: python3 playwright_capture.py site1=https://example.com [site2=https://...]
Output: ./captures/<name>_hero.png, ./captures/<name>_full.png, ./captures/tokens_<name>.json

Validated 2026-08 against WebGL-heavy agency sites (lusion.co, resn.co.nz, owledmedia.com).
"""
import json, re, sys, time
from playwright.sync_api import sync_playwright

def parse_args(argv):
    sites = {}
    for a in argv:
        if "=" in a:
            k, v = a.split("=", 1)
            sites[k] = v
    return sites

TOKEN_JS = """() => {
  const walk = [...document.querySelectorAll('section,div,header,footer,nav,a,button,h1,h2,h3,p,span')].slice(0,400);
  const bg = {}, fg = {};
  walk.forEach(el => {
    const s = getComputedStyle(el);
    if (s.backgroundColor && s.backgroundColor !== 'rgba(0, 0, 0, 0)') bg[s.backgroundColor] = (bg[s.backgroundColor]||0)+1;
    if (s.color) fg[s.color] = (fg[s.color]||0)+1;
  });
  const top = o => Object.entries(o).sort((a,b)=>b[1]-a[1]).slice(0,8).map(e=>e[0]);
  const fonts = new Set();
  document.querySelectorAll('style').forEach(s => {
    (s.textContent.match(/font-family:[^;}]+/g)||[]).forEach(f=>fonts.add(f));
  });
  return {
    title: document.title,
    h1: (document.querySelector('h1')||{}).textContent || null,
    headings: [...document.querySelectorAll('h1,h2')].slice(0,25).map(h=>h.tagName+': '+h.textContent.trim().slice(0,90)),
    bodyFont: getComputedStyle(document.body).fontFamily,
    fontDecls: [...fonts].slice(0,15),
    topBg: top(bg), topFg: top(fg),
    buttons: [...document.querySelectorAll('a[class*=btn],button,a[class*=cta]')].slice(0,10).map(b=>b.textContent.trim().slice(0,50)),
    images: [...document.images].slice(0,15).map(i=>i.src.slice(-80)),
  };
}"""

BOT_TITLES = re.compile(r'just a moment|not supported|attention required|access denied', re.I)

def main():
    sites = parse_args(sys.argv[1:])
    if not sites:
        sys.exit("no sites given; use name=url pairs")
    import pathlib
    out = pathlib.Path("captures"); out.mkdir(exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=[
            "--enable-gpu","--use-gl=angle","--use-angle=swiftshader",
            "--disable-dev-shm-usage","--no-sandbox"])
        ctx = browser.new_context(viewport={"width":1600,"height":900},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36")
        for name, url in sites.items():
            page = ctx.new_page()
            try:
                page.goto(url, timeout=45000, wait_until="domcontentloaded")
                page.wait_for_timeout(10000)  # WebGL/animation settle
                title = page.title()
                if BOT_TITLES.search(title):
                    print(f"BOT-CHECK {name}: title={title!r} — do not analyze, report blocked")
                else:
                    print(f"OK {name} | {title}")
                page.screenshot(path=str(out/f"{name}_hero.png"))
                tokens = page.evaluate(TOKEN_JS)
                tokens["url"], tokens["title"] = url, title
                (out/f"tokens_{name}.json").write_text(json.dumps(tokens, indent=1))
                for i, y in enumerate([900,1800,2700,3600]):
                    page.evaluate(f"window.scrollTo(0,{y})"); page.wait_for_timeout(2500)
                    page.screenshot(path=str(out/f"{name}_sec{i+1}.png"))
                page.screenshot(path=str(out/f"{name}_full.png"), full_page=True)
            except Exception as e:
                print(f"FAIL {name}: {str(e)[:150]}")
            finally:
                page.close()
        browser.close()

if __name__ == "__main__":
    main()
