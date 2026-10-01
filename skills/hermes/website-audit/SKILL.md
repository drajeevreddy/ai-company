---
name: website-audit
description: Audit a website's SEO meta and headers via curl.
version: 0.1.0
author: Rajeev Reddy, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [web, audit, seo, meta, curl]
    related_skills: [headless-site-inspection, site-visual-review]
---

# Website Audit Skill

Audit any website's meta tags, structured data, and HTTP headers using curl — no browser needed.

## When to Use

- User asks to review a website's SEO setup
- User wants to check meta tags, schema.org, Open Graph, Twitter Cards
- User wants to verify security headers (HSTS, CSP, X-Frame-Options)
- User shares a URL and wants a technical analysis

## How to Run

1. Fetch page HTML:
   ```bash
   curl -s -L -m 15 https://example.com/
   ```

2. Extract title:
   ```bash
   curl -s -L -m 15 https://example.com/ | grep -oP '(?<=<title>).*?(?=</title>)'
   ```

3. Extract meta description and all meta content attributes:
   ```bash
   curl -s -L -m 15 https://example.com/ | grep -oP '(?<=<meta name="description" content=").*?(?=")'
   ```

4. Check HTTP headers:
   ```bash
   curl -sI -L -m 15 https://example.com/ | head -n 20
   ```

5. Extract Schema.org JSON-LD:
   ```bash
   curl -s -L -m 15 https://example.com/ | grep -oP '(?<=<script type="application/ld\+json">).*?(?=</script>)'
   ```

6. For subpages: try `curl -s -L -m 15 https://example.com/about`. If it returns 404 with same meta structure as homepage, the site uses JS client-side routing.

## Checklist

- Title present, descriptive, under 60 chars
- Meta description present, compelling, under 160 chars
- OG tags: title, description, image, url, type, site_name
- Twitter cards: card, site, creator, title, description, image
- Canonical present and correct
- Hreflang for multilingual
- Schema.org JSON-LD with @type, @context, name, description
- Security headers: HSTS, CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy

## Pitfalls

- `/about`, `/services`, `/contact` may return 404 on curl but work in browser — usually JS routing, prerender needed for SEO.
- Site may return 403 programmatically but 200 in browser.
- Schema.org founder field may use placeholder text — trust signal gap.
- Always check both page content AND HTTP headers.

## References

- `references/website-meta-audit.md` — meta/header audit checklist
