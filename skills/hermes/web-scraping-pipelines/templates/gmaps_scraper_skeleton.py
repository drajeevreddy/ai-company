"""Google Maps multi-city scraper skeleton (validated Aug 2026).

Copy this file, then modify: QUERIES list, parse_body() field slots if layout
shifted (see references/google-maps-feed.md), and output paths.

Usage: python3 gmaps_scraper_skeleton.py
Crash-safe: appends each query's records to RAW_PATH; re-runs skip completed keys.
"""

import json, os, random, re, time, datetime
from playwright.sync_api import sync_playwright

OUT_DIR = os.path.expanduser("~/scrape_out")
os.makedirs(OUT_DIR, exist_ok=True)
RAW_PATH = os.path.join(OUT_DIR, "raw_places.jsonl")
LOG_PATH = os.path.join(OUT_DIR, "scraper.log")

UA = "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0"

# EDIT ME: geographic x category sweep
CITIES = ["Mumbai", "Delhi", "Bengaluru"]
SPECIALTIES = ["diabetologist"]


def log(msg):
    line = f"[{datetime.datetime.now().isoformat(timespec='seconds')}] {msg}"
    print(line, flush=True)
    with open(LOG_PATH, "a") as f:
        f.write(line + "\n")


def done_keys():
    done = set()
    if os.path.exists(RAW_PATH):
        with open(RAW_PATH) as f:
            for line in f:
                try:
                    rec = json.loads(line)
                    done.add((rec["query_city"], rec["query_specialty"]))
                except Exception:
                    pass
    return done


def find_records(node, out):
    """Place-record signature: long list, slot10='0x..:0x..' fid, slot11=name."""
    if isinstance(node, list):
        if (len(node) > 150 and isinstance(node[10], str) and ":0x" in node[10]
                and isinstance(node[11], str) and node[11]):
            out.append(node)
            return
        for v in node:
            find_records(v, out)


def parse_body(body_text, city, specialty):
    recs = []
    try:
        if body_text.lstrip().startswith("{"):
            env, _ = json.JSONDecoder().raw_decode(body_text.lstrip())
            body_text = env.get("d", "")
        data = json.loads(body_text.split(")]}'", 1)[1].strip())
    except Exception:
        return recs
    found = []
    find_records(data, found)
    for r in found:
        rating = reviews = None
        blk = r[4] if len(r) > 8 else None
        if isinstance(blk, list) and len(blk) > 8:
            if isinstance(blk[7], (int, float)):
                rating = float(blk[7])
            if isinstance(blk[8], int):
                reviews = int(blk[8])
        phones = []
        if len(r) > 178 and isinstance(r[178], list):
            for b in r[178]:
                try:
                    p = b[3]
                    if isinstance(p, str) and re.fullmatch(r"\+?[0-9][0-9 \-\d]{7,15}", p.strip()):
                        pn = re.sub(r"[^\d+]", "", p)
                        if pn not in phones:
                            phones.append(pn)
                except Exception:
                    pass
        address = r[39] if len(r) > 39 and isinstance(r[39], str) else None
        recs.append(dict(
            name=r[11], rating=rating, review_count=reviews,
            category=(r[13][0] if len(r) > 13 and isinstance(r[13], list) and r[13]
                      and isinstance(r[13][0], str) else None),
            phones=phones, address=address, city=city, specialty=specialty,
            place_id=(r[78] if len(r) > 78 and isinstance(r[78], str) else None),
            source="google_maps",
            query=f"{specialty} in {city}",
            scraped_at=datetime.datetime.now().isoformat(timespec="seconds"),
        ))
    return recs


def scrape_query(pg, specialty, city):
    bodies = []

    def on_resp(resp):
        try:
            if "/search?" in resp.url and "tbm=map" in resp.url:
                t = resp.text()
                if len(t) > 5000:
                    bodies.append(t)
        except Exception:
            pass

    pg.on("response", on_resp)
    q = f"{specialty}+in+{city.replace(' ', '+')}"
    try:
        pg.goto(f"https://www.google.com/maps/search/{q}?hl=en&gl=in",
                wait_until="domcontentloaded", timeout=60000)
        pg.wait_for_timeout(random.randint(4000, 6000))
        prev, stable = -1, 0
        for _ in range(60):
            feed = pg.query_selector('div[role="feed"]')
            if not feed:
                log(f"  [{city}/{specialty}] no feed")
                break
            feed.evaluate("el => el.scrollBy(0, el.scrollHeight)")
            pg.wait_for_timeout(random.randint(1800, 3200))
            cnt = feed.evaluate("el => el.querySelectorAll('a[href*=\"/maps/place\"]').length")
            if "reached the end of the list" in pg.content():
                break
            stable = stable + 1 if cnt == prev else 0
            prev = cnt
            if stable >= 3:
                break
    finally:
        try:
            pg.remove_listener("response", on_resp)
        except Exception:
            pass
    recs, seen = [], set()
    for b in bodies:
        for r in parse_body(b, city, specialty):
            k = r["place_id"] or (r["name"], tuple(r["phones"]))
            if k not in seen:
                seen.add(k)
                recs.append(r)
    log(f"  [{city}/{specialty}] bodies={len(bodies)} records={len(recs)}")
    return recs


def main():
    todo = [(c, s) for s in SPECIALTIES for c in CITIES if (c, s) not in done_keys()]
    log(f"START {len(todo)} queries remaining")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True,
                                    args=["--lang=en-US", "--disable-blink-features=AutomationControlled"])
        ctx = browser.new_context(user_agent=UA, locale="en-US",
                                  viewport={"width": 1440, "height": 900},
                                  timezone_id="Asia/Kolkata")
        pg = ctx.new_page()
        for i, (city, spec) in enumerate(todo):
            try:
                recs = scrape_query(pg, spec, city)
                with open(RAW_PATH, "a") as f:
                    for r in recs:
                        f.write(json.dumps(r, ensure_ascii=False) + "\n")
            except Exception as e:
                log(f"  [{city}/{spec}] ERROR: {e}")
                time.sleep(5)
            time.sleep(random.uniform(2.0, 5.0))
        browser.close()
    log("DONE")


if __name__ == "__main__":
    main()
