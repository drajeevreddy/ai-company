---
name: site-visual-review
description: Judge website design visually. Use for hero/UX reviews.
---

# Site Visual Review

Visually inspect or compare live websites via headless Playwright screenshots + native vision review. Use when asked to judge design quality, hero sections, UX, or pick "best looking" sites — works even when the built-in browser stack (camofox) is down.

## Workflow

1. Run `scripts/capture_sites.py` (in this skill) to screenshot one or many live sites:
   `python3 <skill_dir>/scripts/capture_sites.py OUT_DIR name1=https://a.com name2=https://b.com`
   - Writes `OUT_DIR/<name>_hero.png` (after load) and `<name>_settle.png` (after mouse move) per site.
2. Load each PNG with `vision_analyze` (native vision attaches it directly) and ask a SPECIFIC reviewer question, e.g.: "You are a design specialist reviewing this hero: describe the visual concept and any 3D/WebGL elements, typography/layout quality, how memorable the first impression is, and weaknesses."
3. Synthesize a ranked verdict across all reviewed shots against the user's stated criteria (e.g. "most unforgettable 3D experience"), plus transferable patterns observed (interactivity > decoration, one dominant idea per hero, type doing heavy lifting, motion personality).

## Launch configuration that works (validated)

```python
from playwright.sync_api import sync_playwright
browser = p.chromium.launch(headless=True, args=[
    "--enable-gpu", "--use-gl=angle", "--use-angle=swiftshader",
    "--disable-dev-shm-usage", "--no-sandbox"])
ctx = browser.new_context(viewport={"width": 1600, "height": 900},
    user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36")
```

- SwiftShader renders WebGL without a real GPU — adequate for judging layout/concept/motion structure, though shader fidelity differs from end-user hardware.
- Wait ~10–15 s after `goto(..., wait_until="domcontentloaded")` so 3D/WebGL scenes finish booting before the hero shot.

## Pitfalls

- Do NOT sink time into the built-in camofox browser stack: if its server is unreachable, go straight to the Playwright method above.
- Flatpak Chrome `--headless=new --screenshot=` FAILS with "Failed to write file: No such file or directory" for paths outside its sandbox — never use it for screenshots; use Playwright.
- `web_extract` may be search-only depending on backend config (error tells you to set `web.extract_backend`); if you need page TEXT, grab it in the same Playwright pass via `page.content()` instead of fighting backends.
- Font/animation-heavy sites can exceed the default 30 s screenshot timeout ("waiting for fonts to load...") — wrap each site's capture in try/except, print FAIL, continue with the rest.
- Some elite WebGL studios actively block automated/headless browsers (page title becomes "Not Supported" / Cloudflare interstitial "Just a moment..."). Report this as a finding about the site, and verify such sites manually in a normal browser before ranking them.

## References

- `references/award-site-anatomy.md` — ranked world-class 3D agency sites (Lusion/Resn/Noomo...), what makes them unforgettable, and full scoping/cost/phasing for a Lusion-level remake.
