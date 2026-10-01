#!/usr/bin/env python3
"""Screenshot live sites headlessly for visual review.

Usage:
    python3 capture_sites.py OUT_DIR name1=https://a.com name2=https://b.com

Writes OUT_DIR/<name>_hero.png (after load+boot wait) and
OUT_DIR/<name>_settle.png (after a mouse move) per site.
"""
import sys
import os
from playwright.sync_api import sync_playwright

BOOT_WAIT_MS = 12000   # let WebGL/3D scenes boot
SETTLE_WAIT_MS = 3000


def main() -> None:
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    out_dir = sys.argv[1]
    targets = sys.argv[2:]
    os.makedirs(out_dir, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--enable-gpu",
                "--use-gl=angle",
                "--use-angle=swiftshader",
                "--disable-dev-shm-usage",
                "--no-sandbox",
            ],
        )
        ctx = browser.new_context(
            viewport={"width": 1600, "height": 900},
            user_agent=(
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/131.0 Safari/537.36"
            ),
        )
        for target in targets:
            name, _, url = target.partition("=")
            page = ctx.new_page()
            try:
                page.goto(url, timeout=45000, wait_until="domcontentloaded")
                page.wait_for_timeout(BOOT_WAIT_MS)
                hero_path = os.path.join(out_dir, f"{name}_hero.png")
                page.screenshot(path=hero_path)
                page.mouse.move(800, 500)
                page.wait_for_timeout(SETTLE_WAIT_MS)
                settle_path = os.path.join(out_dir, f"{name}_settle.png")
                page.screenshot(path=settle_path)
                title = page.title()
                blocked = title.strip().lower() in {"not supported", "just a moment..."}
                note = " (HEADLESS-BLOCKED — verify manually in a real browser)" if blocked else ""
                print(f"OK {name} | {title}{note}")
            except Exception as e:
                print(f"FAIL {name}: {str(e)[:150]}")
            finally:
                page.close()
        browser.close()


if __name__ == "__main__":
    main()
