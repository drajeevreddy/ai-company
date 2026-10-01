# webcmd Runtime Gotchas (v0.7.x, verified 2026-08-22)

Hard-won specifics from building a working self-healing agent (SlotDeck, ~/slotdeck).
All verified live — not guesses.

## CLI mechanics

- `webcmd session create` (no `-f json`) prints `id: session_<uuid>\nkind: explicit` — parse with `/id:\s*(session_[a-z0-9-]+)/i`. The `-f json` flag on session create may not emit clean JSON.
- `browser run` output: JSON with `{ok, result, logs, page, snapshotDiff, error{code,message,details}, artifacts[]}`. If stdout has leading banner text, slice from first `{`.
- Default execution timeout 30s; pass `--timeout <seconds>` to browser run AND wrap the execFile call with a larger Node timeout.
- Session ids are opaque; store and reuse one shared session across missions (cheaper than per-mission sessions).

## Artifacts (screenshots etc.)

- Screenshot paths in programs must be **relative logical filenames** (`page.screenshot({path: 'shot.png'})`). Absolute paths or any `..` → `BROWSER_RUN_INVALID_INPUT: "Artifact paths must be relative logical filenames"`.
- Artifacts land under `~/.webcmd/cache/browser-run/<artifactId>/<filename>` — the response's `artifacts[].locator` is `browser-run://<artifactId>/<filename>`; find the real file by globbing that cache dir.

## Program context rules (the #1 source of failures)

- The program body runs in a **Node-like sandbox with a Playwright `page`**, NOT inside the browser. Bare `document` / `window` / `fetch` references throw immediately (exit code 1, "Command failed").
- DOM access ONLY via `await page.evaluate(() => {...})`, elements via `await page.$$(sel)` / `page.$(sel)`.
- Values from your orchestrator must be interpolated as JSON literals: `JSON.stringify(opts.time)`, never raw template splices.

## Waiting / navigation

- Never `waitUntil: 'networkidle'` against any page holding an open SSE/WebSocket connection (live dashboards) — it times out at 30s every time. Use `domcontentloaded` + `waitForTimeout(ms)`.
- For form submissions that fire fetch(), use `Promise.all([page.waitForResponse(r => r.url().includes('/api/...')), page.click(submitSel)])` then read the page's result state (e.g. `window.__BOOKING_RESULT__` set by the site's own script) via page.evaluate.

## Honest token accounting

- Adapter-path tokens ≈ bytes/4 summed over program strings sent + JSON results returned. Baseline = ONE real full-page DOM snapshot (`page.content()`) through webcmd × 10 naive reasoning steps. Measured example: 12,230 baseline vs 2,886 actual = −76%. Compare mission DELTAS (snapshot tokensUsed before/after), never cumulative-session totals against single-run baselines — that produces nonsense like "−0% saved" or negative savings.
- webcmd emits CloakBrowser banners (free-tier upsell) on some commands — ignore stdout noise before the JSON.

## Escaping: the #2 source of failures (string-interpolated evaluate bodies)

- NEVER build `page.evaluate` bodies by string-concatenating data (queries, tokens) into the JS source. Backslash escaping through the generator layers gets doubled silently: source `\\d` ⇒ emitted regex `\d`-as-literal-backslash ⇒ regexes match NOTHING, extraction returns 0 results with no error. Cost a full debugging cycle (5+ probe programs) in one session.
- Correct pattern — pass data as an evaluate ARGUMENT:
  `return await page.evaluate((qTokens) => { ...regexes single-escaped in ONE place... }, JSON.parse('["thyronorm","50"]'));`
- Debugging loop that finds it fast: replicate the generated program inline via a temp file, run both, diff `JSON.stringify(suspectLine)` of emitted source lines to see the real escaping.

## Output size

- `browser run` result cap is 65536 chars → `BROWSER_RUN_OUTPUT_LIMIT`. Raise with `--max-output <chars>` (1200000 works) for base64/bulk extraction; pull big blobs in ~700KB slices per run.

## Real-site scraping patterns (Indian pharmacies, verified live via webcmd stealth browser)

- 1mg, PharmEasy, Apollo 24|7 all render through CloakBrowser without bot walls. Apollo serves an empty `<title>` but products DO render — don't gate success on title.
- Lazy-loaded grids (Apollo) need scroll: `scrollTo(0,900)` → wait 3s → `scrollTo(0,1800)` → wait 2s before extracting.
- Text-line pairing extractor that works across all three layouts: a price line (`₹…`) pairs with the most recent line passing a medicine-name regex (tablet/capsule/bottle/mcg/mg…), filtered by NOISE_RE (`^discounted price$`, `^add( to cart)?$`, …) and JUNK_RE (coupons, "per tablet", manufacturer suffixes). CRITICAL guard: pack-size lines ("120 Tablet(s) in Bottle", "bottle of 120 tablets") pass the name regex and MUST be skipped (`PACK_RE` → continue) or they overwrite the brand candidate and the relevance gate rejects everything.
- Distance-window the pairing (skip price if >8 lines since last name) — first price after a name wins, then reset the candidate.
- Checkout on real pharmacies stays a deep link (login + Rx required) — scrape/compare prices, don't automate past auth/prescription walls.

## Dashboard layout overflow (CSS)

- Grid dashboards where a bottom card row renders off-viewport: give `main` explicit `grid-template-rows: minmax(0,1fr) auto auto` + `overflow:hidden`, tag each row (`grid-row: 2/3`), and put `min-height:0` on every scrollable child. Without `minmax(0,1fr)`, content rows force the last row past the fold.

## Self-healing loop pattern (proven)

- Compile adapters from captured sitemap memory into selector PLANS (attribute-preferred: `[data-field=x]` > `#id` > `[name=y]`); tag memory with the world variant it was captured from; treat memory-vs-world variant mismatch as "stale" → pre-emptive heal.
- Distinguish business rejections (slot full, duplicate booking — structured `{ok:false, stage:'slot_pick'}`) from DOM breaks (selector miss, timeout) — only the latter triggers healing; surfacing business rejections honestly matters for demo credibility.
- Chaos testing: break BETWEEN two successful adapter runs so the stale adapter provably fails first (break-then-explore-from-scratch hides the healing loop because the fresh explore captures the new DOM). Timed sequence observed: detect ~0.9s, wipe→re-explore→recompile→recover ~3s total.

## Visual verification of agent dashboards

When the panel is fed by SSE: screenshot with `domcontentloaded` + fixed wait, review with vision_analyze, iterate. Common issues found this way: stale-event toasts replaying on page load (gate routing by event timestamp vs boot time), token-economy cards comparing wrong quantities, scrollbars clipping CTA buttons, radar blips clumping (use golden-angle placement), sparklines rendering as slabs (cap bar width).
