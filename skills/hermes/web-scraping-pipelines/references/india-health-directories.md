# Indian Doctor-Directory Source Triage (Aug 2026)

Findings from probing major sources for diabetologist/endocrinologist listings with
rating, review count, phone. Re-validate before reuse — sites change defenses.

## curl-friendly (plain HTTP + Firefox UA)

| Source | Status | Fields available | Notes |
|---|---|---|---|
| practo.com/<city>/<specialty> | 200 | name, profile URL, clinic address (ld+json), story counts | **No star rating, no real phones** (phones are asset-hash fragments). ~10 doctors/page, `?page=N` pagination works. JSON-LD `Physician` blocks per card. |
| sulekha.com/diabetologists/<city> | 200 | name, locality, per-doctor "contact-address" page links | Listing cards carry no per-doctor rating; only a city-level aggregateRating in ld+json. Contact pages may yield phones but need per-doctor fetches. |
| vaidam.com | 200 | nothing useful | JS shell; no doctor data server-side. |
| medindia.net practitioners | 404 | — | Old practitioner index gone. |
| drlogy.com | 404 | — | No such listing path. |
| bajajfinservhealth.in | 404 | — | Search/listing paths not indexable. |

## Bot-walled / JS-only for curl

| Source | Behavior | Workaround |
|---|---|---|
| justdial.com | 200 but 14-byte empty `<HTML></HTML>` shell even with cookie warm-up + Referer | Needs full browser render; not attempted further once Maps proved sufficient |
| credihealth.com | 403 to curl | Untested headless |
| lybrate.com listing pages | Next.js shell with `statusCode` 404 inside `__NEXT_DATA__`; alternate URLs 504 | Dead as of this date |
| skedoc.com | curl HTTP/2 protocol error (`keep-alive` header violation) | Untested |

## Google Maps (recommended primary)

Carries ALL of: star rating, review count, clinic phone, full address, category —
the only source where the user's typical filter criteria (5★, ≥50 reviews) exist
natively per record. Extraction via feed interception:
see references/google-maps-feed.md.

## Practical guidance

- If the task requires ratings/review-counts/phones, go straight to Google Maps;
  the directories either lack the fields or hide phones behind call-widgets.
- Practo is a good SECONDARY for cross-checking names/specialties in a specific
  city (its listing is deterministic and paginated), but cannot supply phones.
- Justdial's vote counts differ from Google's review counts — never mix sources
  in one numeric column without labeling provenance.

## Individual doctor-direct mobile numbers (Aug 2026 verdict)

No Indian aggregator publishes doctors' personal mobiles — all route through
paid call-connect; this is by design and TRAI/DPDP-constrained. Probed live:
Practo clinic JSON-LD `telephone` is server-side PRE-masked (`+914****2962`)
even before rendering, profile pages have no tel: links at all; Sulekha page
JSON has `"mobile":"", "phoneNumber":null` (its 90032xxxxx hits are its own
call-connect); Apollo repeats one Bangalore 080 call-center site-wide via
`tel:` hrefs; Meddco/Vijaya/Kauvery numbers are switchboards in nav menus;
Justdial's WAF kills even headless Chromium with ERR_HTTP2_PROTOCOL_ERROR.
The closest legitimate "direct doctor number" is the practice's own line on
Google Maps — sweep "<specialty> doctor clinic in <city>" queries; practices
named after their doctor carry that practice's reception/direct line.
When normalizing phones, treat 1800/1860 prefixes as chain call-center
toll-frees (format `1860-500-1066`, exclude from any "direct lines" sheet)
— Maps lists them alongside real direct lines.

## Recovering a DEAD/legacy site the owner controls (Aug 2026)

Workflow that fully recovered a WordPress corporate site (madhumehahealthcare.com):

1. Probe `<site>/robots.txt` + `<site>/sitemap.xml` first — WP exposes
   `wp-sitemap.xml` with per-post-type sitemaps giving the complete URL list.
2. Try the WP REST API (`/wp-json/wp/v2/pages?per_page=100&_embed`) BEFORE any
   HTML scraping — structured JSON beats HTML parsing when it works.
   **LiteSpeed pitfall:** some LiteSpeed-cached WP sites serve CORRUPTED JSON for
   specific URL shapes (observed: any `per_page=100` request consistently returned
   raw page text instead of JSON while small requests passed; cache-busting
   params did NOT help — poisoned cache entry). Test `_fields=id,title` first;
   if big requests are corrupt but small pass, abandon wp-json and scrape
   rendered HTML from the sitemap URL list instead.
3. For each URL save BOTH raw HTML (fidelity reference) AND clean Markdown
   (html2text on the `div.entry-content`/`main` node) + front-matter metadata
   (title, meta description, nav links extracted from the page).
4. Image recovery: grep ALL raw HTML for every img/pdf reference — content-node
   extraction misses header sliders and icons. Dead-hotlinked images (old dev
   pointed at a defunct sibling domain) are often recoverable via Wayback:
   `archive.org/wayback/available?url=` per exact URL (`.../web/<ts>id_/` prefix
   returns original bytes), then CDX wildcard search
   (`web.archive.org/cdx/search/cdx?url=domain/path*&collapse=urlkey`), then
   host variants (www/non-www, http/https — indexed separately). Accept total
   loss quickly; document exactly what's gone and why in the deliverable.
5. Deliverable shape that worked: archive dir (`pages/*.md`, `posts/*.md`,
   `raw_html/*.html`, `media/`, `manifest.json`) + REBUILD_BRIEF.md (site map,
   page inventory w/ content sizes, media inventory incl. lost files + why,
   functional notes e.g. "form was Contact Form 7") + BUILD_PROMPT.md — a
   complete agent-ready rebuild spec (design system, animation spec, tech stack,
   real recovered copy inline, acceptance checklist) so "rebuild my site"
   becomes one prompt handoff.
