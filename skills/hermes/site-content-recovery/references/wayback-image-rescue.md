# Wayback Machine Image Rescue (dead-hotlinked images)

Abandoned sites often hotlink images from domains that no longer resolve.
The Internet Archive is the only realistic recovery source. Work the ladder
in order; stop at first hit. Every step below was exercised Aug 2026 on
nutrivisor.co.in / orangerx.net assets — outcome noted per step.

## Ladder

1. **Snapshot availability API** (fastest, exact URL):
   `http://archive.org/wayback/available?url=<EXACT_ORIGINAL_URL>`
   → `archived_snapshots.closest` gives `{timestamp, status}`.
   Fetch original bytes with the `id_` flag (skips archive toolbar/wrapping):
   `https://web.archive.org/web/<TIMESTAMP>id_/<ORIGINAL_URL>`
   Validate body ≥ ~500 bytes before saving (error pages can be tiny).
   Outcome Aug 2026: recovered 1 of 10 files this way.

2. **URL variants** — Wayback indexes hosts separately. Retry step 1 with:
   non-www ↔ www, http ↔ https, trailing-slash variants of the path.
   Outcome Aug 2026: no extra hits, but costs seconds — always worth trying.

3. **CDX wildcard index** — see everything archived under a directory:
   `http://web.archive.org/cdx/search/cdx?url=<DOMAIN>/<PATH>/*&output=json&collapse=urlkey&filter=statuscode:200&limit=40`
   Rows: `[urlkey, timestamp, original, mimetype, statuscode, digest, length]`.
   Useful both to find sibling captures AND to confirm what does NOT exist.
   Note: web.archive.org CDX can time out on broad wildcards; retry once,
   then narrow the pattern (`uploads/2014/12*` beats `domain/*`).
   Outcome Aug 2026: found 7 sibling files but none of ours — proves the
   crawler saw that folder yet never fetched our specific images.

## When it's provably lost

If exact-URL availability checks fail across host/scheme variants AND the CDX
index shows no capture of the file (while showing other files from the same
directory), the asset was never crawled. Say so plainly in the deliverable:
list each lost file with the page(s) it appeared on, and give practical
replacements (old dev backups, reshoot, generic icon). Do NOT keep polling.

## Politeness

~1–1.5 s between archive requests; web.archive.org downloads are slow —
timeout ≥ 90 s for binary fetches.
