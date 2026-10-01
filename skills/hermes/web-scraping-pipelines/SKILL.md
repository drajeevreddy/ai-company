---
name: web-scraping-pipelines
description: "Use when scraping listing/directory data at scale."
version: 1.0.0
category: software-development
---

# Web Scraping Pipelines

Extract thousands of structured records (businesses, doctors, listings) from sites
that hide their data behind JS shells, bot walls, or internal RPC feeds, and deliver
a verified spreadsheet.

## When to Use
- User asks to "scrape all X", "build a list/database of Y at scale", or extract
  tabular data (names, phones, ratings, addresses) from directory/listing sites.
- Target site renders client-side or serves data via internal JSON endpoints.

## Workflow

1. **Probe sources with plain curl FIRST (cheap, seconds).** Check HTTP code AND
   whether real record markers exist in the body (search for sample names, `"Dr."`,
   `ld+json`, store-name classes). A 200 with an empty `<HTML></HTML>` shell or a
   JS-only page = dead end for curl. See references/india-health-directories.md
   for a worked triage of Indian doctor directories.
2. **Pick the source whose data layer carries ALL required fields natively.**
   If the user filters by rating/review-count/phone, only scrape sources where
   those fields are in the payload — do not plan to join across sources.
3. **If the site is a JS shell, intercept its internal feed with Playwright**
   (headless Chromium), not DOM scraping. Load the public URL, attach
   `page.on("response")`, filter for the data endpoint, scroll/paginate to
   exhaustion, parse captured bodies offline. See references/google-maps-feed.md
   for the full Google Maps recipe (field layout, envelope formats, parser).
4. **Checkpoint every batch to JSONL** keyed by (query-city, query-specialty) so a
   crashed run resumes where it stopped. Log progress per query to a .log file.
5. **Dedupe, normalize, deliver.** Dedupe on place_id (fallback: name+address
   prefix). Normalize phones to E.164 (+91XXXXXXXXXX). Build the workbook with
   openpyxl: strict-filter sheet + near-top sheet (4.7–4.9★ so borderline entries
   survive a strict cutoff) + all-records sheet + summary sheet with real SUM
   formulas. Run the xlsx skill's recalc.py before delivering.

## Pitfalls

- **curl 200 ≠ scrapable.** Justdial returns 200 with a 14-byte empty shell to
  non-browser clients; Lybrate returned a Next.js 404 shell. Always grep the body
  for actual record content before committing to a source.
- **UI pages are shells; data lives in XHR/fetch responses.** Google Maps'
  `/maps/search/...` HTML contains zero place names. The data arrives via
  `google.com/search?tbm=map&...&pb=...` responses — capture those.
- **Two response envelope formats** from the same endpoint: raw `)]}'`-prefixed
  JSON-lines AND `{"c":0,"d":"..."}/*""*/` wrappers. Parse with
  `json.JSONDecoder().raw_decode()` (trailing `/*""*/` breaks plain `json.loads`).
- **Feed caps around 120 results per query.** For "all of India" coverage, sweep
  many geographic sub-queries (city list) × specialty, then dedupe globally.
- **Scroll until the end-marker** ("reached the end of the list" in page content)
  or link count is stable for 3 consecutive scrolls; otherwise you silently stop
  at page 1 (20 records).
- **Terminal output masks long digit strings** (phones show as +917****8711) even
  when the underlying data is perfect. Never judge phone integrity from terminal
  echo — write a verification report to a file and read the file.
- **Verification must mirror dedupe semantics.** When the builder keeps the FIRST
  occurrence per dedupe key but raw JSONL holds later duplicates from other
  queries, comparing workbook rows against the LAST raw occurrence yields false
  mismatches. Build the raw lookup with `if key not in map` (first-wins), same
  as the builder, before spot-checking.
- **Phone regex hits in search-engine HTML are frequently false positives** —
  e.g. 10-digit substrings inside base64 redirect hashes on Bing result pages.
  Before counting a source as "has phones", grep surrounding context and confirm
  the number appears as a rendered/labelled value, not embedded in URLs/hashes.
- **`playwright install chromium --with-deps` needs interactive sudo** and fails on
  Fedora under agents. Plain `python3 -m playwright install chromium` works; the
  "OS not officially supported / fallback build" warning is benign.
- **Rate politely:** 2–5 s jitter between queries, 1.8–3.2 s between scrolls;
  a 140-query sweep completes in ~90 min without blocks.

## Support Files
- references/google-maps-feed.md — response envelope formats, place-record field
- references/nextjs-rsc-extraction.md — extracting structured JSON from Next.js App Router sites via RSC protocol (bypassing JS shells, randomized offset pagination)
  layout ([11]=name, [4][7]=rating, [4][8]=reviews, [178][n][3]=phone), parser code.
- references/india-health-directories.md — which Indian doctor-directory sources
  yield data to curl vs headless, and what fields each exposes.
- templates/gmaps_scraper_skeleton.py — working crash-safe multi-city scraper
  skeleton; copy and modify query lists/parsers.
