---
name: seo-content-creation
description: Create SEO content for websites.
---

# SEO Content Creation

## Trigger
Use when the user needs SEO-optimized content for a website — especially medical/healthcare clinics, local businesses, or professional services. Covers blog posts, meta descriptions, schema markup, directory profiles, and technical SEO audits.

## Workflow

### Phase 1: Audit & Discovery
1. Check existing website structure, pages, and current search rankings
2. Identify target keywords (primary + long-tail, location-based)
3. Audit existing Google Business Profile listings (NAP consistency, photos, services)
4. Check current directory listings (Practo, Lybrate, JustDial, HexaHealth, etc.)
5. Run technical SEO checks: page speed, mobile-friendliness, crawl errors, sitemap

### Phase 2: On-Page SEO Content
1. Write unique meta titles (<60 chars) and meta descriptions (150-160 chars) for every page
2. Create keyword-rich H1 headings (one per page)
3. Write body content (600-1000 words) with natural keyword distribution
4. Add FAQ sections with FAQPage schema on key pages
5. Optimize URL structure: clean, keyword-rich, hyphenated
6. Add internal linking between related pages

### Phase 3: Structured Data
1. Generate JSON-LD schema markup for LocalBusiness, Physician, FAQPage, BreadcrumbList
2. Validate schema with Google Rich Results Test
3. Add schema to each page's <head> or before </body>

### Phase 4: Blog Content (2 posts/week)
1. Create keyword-targeted blog posts targeting high-intent search queries
2. Each post must include: SEO title, meta description, H1, 600-1000 words, FAQ section, internal links, CTA
3. Publish on the website CMS
4. Promote on LinkedIn, Facebook, Instagram, WhatsApp

### Phase 5: Directory & GBP Optimization
1. Claim/verify Google Business Profile for each clinic location
2. Ensure NAP consistency across all directory listings
3. Upload photos, services, and hours to each GBP listing
4. Create/update doctor profiles on Practo, Lybrate, 365Doctor, HexaHealth, Credihealth, etc.
5. Post weekly GBP content (health tips, patient testimonials, clinic updates)
6. Implement review generation strategy (ask every patient, share review link via WhatsApp)

### Phase 6: Tracking & Iteration
1. Set up Google Search Console and Google Analytics 4
2. Track impressions, clicks, average position weekly
3. Track GBP views, clicks, direction requests
4. Monitor keyword rankings monthly
5. Adjust content strategy based on performance data

## Pitfalls
- **Duplicate meta titles/descriptions** across pages — always write unique ones per page
- **Keyword stuffing** — distribute keywords naturally; prioritize readability
- **Inconsistent NAP** across directories — this destroys local SEO; maintain identical name, address, phone everywhere
- **Skipping schema validation** — always test JSON-LD with Google Rich Results Test before deploying
- **Ignoring GBP reviews** — reviews are the #1 local ranking factor; make asking for reviews a standard post-consultation step
- **One-time blog publishing** — SEO content requires consistent, ongoing publication (2/week minimum)
- **Not tracking results** — without Search Console and GA4, you cannot measure what is working
- **Canonical/sitemap mismatch** — sitemap URLs must exactly match canonical tags (trailing slashes vs .html); verify with grep before deploy
- **Design system drift** — SEO pages must match main site aesthetics (CSS, JS, animations, nav, footer); extract live site design system before building
- **.htaccess rewrite conflicts** — pretty URL rewrites can break static file delivery; test sitemap.xml/robots.txt/llms.txt return 200 before submitting to GSC
- **CSP header blocking** — over-restrictive Content-Security-Policy can block CDN scripts (GSAP, Lenis); use 'unsafe-inline' for inline scripts, allow cdnjs/unpkg
- **Email/contact consistency** — verify all contact info matches live site (user corrected hello@ → rajeevreddy@quivane.in)

## Key Principles
- Every page needs a unique title tag and meta description
- Doctor profiles on directories must be complete with photo, qualifications, experience, and OPD timings
- Blog posts should target long-tail keywords with local intent (e.g., "endocrinologist in HSR Layout Bangalore")
- Schema markup enables rich results in Google — LocalBusiness, Physician, and FAQPage schemas are essential for medical clinics
- GBP optimization with consistent NAP and regular posts is the fastest path to local search visibility

## Support Files
- `references/blog-posts.md` — Blog posting schedule, checklist, and templates for Shashi Advanced Health
- `references/schema-markup-examples.md` — JSON-LD schema examples (LocalBusiness, Physician, FAQPage)
- `references/directory-listings.md` — Directory listings checklist, NAP consistency rules, GBP content calendar