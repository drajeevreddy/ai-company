---
name: brand-recovery
description: Recover logo & theme from a down or expired website.
---

# Brand Recovery From a Dead Site

Workflow for: owner says "my website is down, pull the logo and the theme so we can rebuild." Validated end-to-end on adorycreatives.com (Aug 2026): domain expired, zero archives, brand fully reconstructed anyway.

## Step 1 — Diagnose WHY it's down (before touching assets)

1. `curl -s -o /dev/null -w "%{http_code}" -L https://<domain>/` — note code (000 = TCP/TLS dead).
2. `dig +short <domain> NS` — **`ns1.dns-expired.com` / `ns2.dns-expired.com` = domain registration EXPIRED**. Also try `dig +short <domain> A`.
3. Fetch over plain HTTP too: expired registrars often serve a parking page titled "Your domain is expired" with HTTP 200 (server: hcdn) while HTTPS fails. A 200 does NOT mean the site is alive — read the body.
4. If expired: tell the user to renew at the registrar FIRST (~₹1k / $12). Everything else is parallel work, not blocked.

## Step 2 — Hunt archived/third-party copies (timebox this)

- Wayback: `https://archive.org/wayback/available?url=<domain>` AND the CDX API (`web.archive.org/cdx/search/cdx?url=<domain>*&output=json`). Young domains (under ~2y) frequently have ZERO snapshots — confirmed twice now. When both come back empty, stop immediately; do not retry-loop (archive.org also 429s fast).
- SEO audit sites cache title/meta description even for dead domains: search `<domain>` + "seo audit", then curl the audit page and grep for og:title/description. This recovers the positioning copy verbatim.
- Google favicon cache `https://www.google.com/s2/favicons?domain=<domain>&sz=256` — sometimes returns HTML instead of PNG when nothing is cached; `file` the download to check before using.
- Social profiles (Instagram/Facebook/LinkedIn) carry bio copy, tagline, contact email, follower counts — searchable via web_search `"brandname" instagram`.

## Step 3 — Ask the user for the logo (fastest path, do it early)

The owner almost always has the logo on their phone or in an old Instagram post. One message beats 30 minutes of cache archaeology. Low-res JPG (150×150) is fine to START from — flag that print/retina needs an SVG recreation later.

## Step 4 — Extract theme tokens from the logo image

Run `scripts/palette_extract.py <logo_image>` (in this skill). It prints JSON with size, top colors, ink, accent, background.

Reading the output:
- `ink` = wordmark/icon color (avg of darkest pixels)
- `background` = paper/canvas tone
- `accent` = most saturated pixel — for MONOCHROME logos this returns a meaningless gray. Don't fake it: propose 1–2 fresh accents and label them `accent_proposed` in the theme file.
- Logos smaller than ~300px: note "vector recreation needed" as a checklist item.

Write findings to `brand/theme.json`: palette, typography direction read off the logo (serif vs sans, case, weight), motion language, and the brand CONCEPT — mine the logo's iconography for a metaphor (a film-slate logo → cinematic site concept; that idea shaped the whole rebuild plan).

## Step 5 — Capture the client/work roster

Users often paste client lists as raw WhatsApp text (URLs per line, mixed senders). Paste files land in `~/.hermes/pastes/` — read_file them, parse handles out of URLs, and write structured JSON with a `vertical` field per client (auto/jewellery/weddings/food...). Verticals drive the site's work-grid IA later.

## Step 6 — Scaffold the project folder

```
<project>/
  PLAN.md          # situation, concept, tiered scope, immediate checklist
  brand/
    logo-original.(jpg|png)
    theme.json
  clients/
    clients.json
  website/         # scaffold lands here later
  brand-recovery/  # scratch: cache dumps, favicon attempts
```

## Pitfalls

- HTTP 200 ≠ site alive. Read the body — expired-domain parking pages return 200.
- Wayback empties are common for young domains; two API shapes (availability + CDX) both empty = move on.
- archive.org rate-limits aggressively (429 on rapid sequential curls) — space requests, don't hammer.
- Google favicon endpoint silently returns HTML on miss — verify with `file`, never trust the extension.
- Monochrome logos have no accent color; proposing one is your job, marked as a proposal.
- Put the renewal action at the TOP of any plan/checklist you hand back — it blocks launch and only the user can do it.
