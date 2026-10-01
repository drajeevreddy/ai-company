# Worked example: qsend.cc reconnaissance (Aug 2026)

User question: "analyze this website ... whats this platform actually based on" — then corrected to "i just need to know whats the platform like what does it acutally do" (i.e. plain-language answer first).

## Answer given (the shape the user wanted)

- WHAT: digital business card + instant follow-up CRM — cards/links/QR, mini CRM (hot/warm/cold), AI email + WhatsApp follow-up sequences, proposals/e-sign, per-rep telemetry. Comparable to Blinq/HiHello/Popl + Linktree + follow-up automation.
- WHO: TRUSTCV LTD, UK company no. 16280940 (Milton Keynes), same group as trustcv.com. Homepage "case study" brands (repairmycar.io, memss.co.uk, fxmaster.co.uk, besttransfers.co.uk, justgive10.com) are their own properties — self-referential social proof.
- BUILT ON: Next.js/React frontend with AI-builder signatures (Lovable error hook + GPT Engineer asset CDN), hosted on Azure UK South behind ASP.NET header, Namecheap domain registered 2026-07-10 (weeks old at analysis time).

## Evidence trail (what the forensics showed)

1. `curl -sI https://qsend.cc/` → `x-powered-by: ASP.NET`, HTTP/2 200.
2. `dig +short qsend.cc A` → 51.140.116.106; ARIN RDAP → Azure (registration 1991, Azure UK South range).
3. `whois qsend.cc` → Namecheap, created 2026-07-10T18:52:31Z, NS = registrar-servers.com (Namecheap default).
4. HTML saved to /tmp/qsend.html: `<html lang="en" dir="ltr">`, `data-precedence` CSS, `<!--$-->` RSC streaming marker, `/assets/styles-*.css`, `<script type="module" src="/assets/index-*.js">` (Vite-style, not /_next/), JSON-LD Organization block: "legalName":"TRUSTCV LTD", "identifier":"Company No. 16280940", GB address, GBP pricing.
5. og:image URL → `https://storage.googleapis.com/gpt-engineer-file-uploads/OV8RQeUES3RKl2TEue1AKb8mvaF2/social-images/social-*.webp` → GPT Engineer asset hosting. Note: GCS bucket (x-goog-* headers) confirmed.
6. `curl -s https://qsend.cc/assets/index-DzOLaELA.js` (750 KB) → `grep -ao` hits:
   - `window.__lovableEvents?.captureException` with `source:"react_error_boundary"` → Lovable-generated app signature
   - `Next.js`, `hydrateRoot` → React/Next.js
7. `robots.txt` disallows /auth, /callback/, /unsubscribe, /app, /admin (private surfaces).
8. Companies House search → TRUSTCV LTD, active, Milton Keynes. trustcv.com itself is static HTML on Microsoft-IIS/10.0 + ASP.NET (same operator, different stack).

## Key signatures to reuse

| Signature | Meaning |
|---|---|
| `window.__lovableEvents?.captureException` + `react_error_boundary` | Lovable AI builder |
| `storage.googleapis.com/gpt-engineer-file-uploads/` in og:image/asset URLs | GPT Engineer asset CDN |
| `data-precedence` + `<!--$-->` + `/assets/*.js` (non-_next) | React 19 RSC / Vite-style bundle |
| `x-powered-by: ASP.NET` + Azure IP + static HTML | Classic Azure App Service; does NOT mean .NET app — verify bundle |
| JSON-LD Organization `legalName` + `identifier` (company no.) | Fastest route to operator identity |

## Traps hit during this run

- `web_extract` refused qsend.cc with "Blocked: URL targets a private or internal network address" — false positive; curl worked fine.
- First response was too forensic-first; user interrupted with "i just need to know whats the platform like" → always lead with plain-language WHAT/WHO/BUILT-ON.
