---
name: website-reconnaissance
description: Use when asked what a website is or what it's built on.
---

# Website / Platform Reconnaissance

Use when the user asks to "analyze this website", "what is this platform actually", "what is X based on", or wants to know who operates an unfamiliar site. Goal: answer three questions — WHAT it does, WHO runs it, WHAT it's built on.

## Output shape (user preference — do not skip)

Lead with the plain-language answer:

1. WHAT it does — one or two lines in product terms (e.g. "digital business cards + instant follow-up CRM").
2. WHO operates it — legal entity from JSON-LD/registry, and any tell (domain age, brand strip).
3. WHAT it's built on — one line (framework, hosting, AI-builder signatures if present).

Then append the technical evidence briefly. Do NOT open with raw headers, DNS output, or grep results — the user asked what the site IS, not for a forensics dump. If the user follows up wanting depth ("show me how you know"), that's when the raw evidence comes out. A user asking to "just tell me what it does" after a verbose reply means the first answer buried the lede — repeat the plain-language version immediately and keep the forensics to one short section.

## Investigation recipe

1. **Plain read first**: `curl -s <url> -o /tmp/site.html` then read it. Extract title, meta description, and the JSON-LD block (`<script type="application/ld+json">`) — the Organization entry often names the legal entity, country, and contact. Note the nav/feature copy: the product is usually self-describing.
2. **HTTP headers**: `curl -sI <url> -H "User-Agent: Mozilla/5.0 ..."`. Look at `x-powered-by`, `server`.
3. **DNS + registration**: `dig +short <domain> A NS MX`; `whois <domain>` for registrar and creation date (fresh Namecheap domain = recently launched project — say so). For IP ownership use ARIN RDAP (`whois.arin.net/rest/ip/<ip>.json`) to identify Azure/AWS/Cloudflare hosting.
4. **Framework markers in HTML**: `data-precedence` attributes + `<!--$-->` streaming markers + `/_next/` assets = Next.js/React; hashed `/assets/index-*.js` = Vite-style bundles; `hydrateRoot`/`createRoot` in the bundle confirms React.
5. **JS bundle fingerprinting**: fetch the main bundle (src from the HTML) and grep for builder signatures:
   - `window.__lovableEvents` / `react_error_boundary` → built with **Lovable**
   - `storage.googleapis.com/gpt-engineer-file-uploads/...` (also in og:image URLs) → assets hosted via **GPT Engineer**
   - `__NEXT_DATA__`, `Next.js`, `next.` strings → Next.js
6. **Operator lookup**: UK entity → Companies House at `find-and-update.company-information.service.gov.uk/company/<company-no>`; also plain web search for the legal name.
7. **Cross-check**: on a brand-new platform, sites listed as "customers / case studies / running the loop" on the homepage are frequently the operator's own properties — verify, don't assume third-party social proof.

## Pitfalls

- **Expired-domain signature**: NS records pointing at `ns1.dns-expired.com` / `ns2.dns-expired.com` mean the registration lapsed — the site isn't hacked or migrated, the OWNER forgot to renew. The registrar serves a "Your domain is expired" parking page over plain HTTP (often with HTTP 200; read the body) while HTTPS fails entirely. Tell the user to renew at their registrar; see skill `brand-recovery` for recovering brand assets from such sites.
- `web_extract` may refuse a perfectly public URL with "Blocked: URL targets a private or internal network address" — that's a false positive. Fall back to `curl` + `read_file` on the saved HTML.
- `x-powered-by: ASP.NET` on an Azure IP does NOT imply the app is .NET — Azure App Service emits this header for Node/Next.js apps too. Confirm the real framework from the bundle/HTML before claiming anything.
- Grep can report "binary file matches" on minified JS — use `grep -ao` (treat-binary-as-text) so signatures aren't missed.
- Don't name a "platform" from one clue. Require two independent signals (e.g. bundle signature + asset-host pattern) before naming a builder.

## References

- `references/qsendlovable-example.md` — full worked example: qsend.cc (digital business card + follow-up CRM by TRUSTCV LTD, Next.js, Lovable/GPT-Engineer signatures, Azure UK South).