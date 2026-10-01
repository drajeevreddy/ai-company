---
name: social-page-audit
description: Audit social pages from screenshots and captions.
version: 0.1.0
author: Rajeev Reddy, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [social-media, audit, vision, growth]
    related_skills: [xurl, site-visual-review]
---

# Social Page Audit Skill

Analyze public social-media pages, captions, and visual assets to produce an audit report with AI video prompt ideas and growth actions.

## When to Use

- User shares a social profile URL and wants an analysis
- User shares screenshots/captions and wants content recommendations
- User asks for AI video/reel prompt ideas to grow a page

## Prerequisites

- `vision_analyze` tool for screenshots/images
- `web_extract` or `browser_navigate` for public pages
- Optional: `write_file` for PDF export

## How to Run

1. If a URL is provided, try to extract public page content with `web_extract` or `browser_navigate`.
2. If screenshots are provided, analyze them with `vision_analyze`.
3. Read captions/post types if supplied by the user.
4. Produce: audit bullets, weak spots, content pillars, and AI video prompt bank.
5. Optionally export to PDF with `write_file` if supported in environment.

## Procedure

1. Collect inputs: URL, screenshots, captions, metrics the user shares.
2. Run visual analysis on screenshots using `vision_analyze` with specific questions about brand clarity, hook strength, text overlay, CTA presence, and consistency.
3. Analyze captions for hook formula, CTA presence, hashtag strategy, and readability.
4. Synthesize an audit with: what’s working, what’s missing, quick wins, and 10–20 AI video prompts tailored to the niche.
5. If requested, write a markdown/PDF deliverable.

## Outputs

- Page audit summary
- Content gap analysis
- AI video/reel prompt bank
- 30-day growth action list

## Pitfalls

- Many platforms block scraping; use screenshots when extraction fails.
- Avoid generic advice; tailor prompts to the actual niche observed.
- Do not invent metrics if user did not provide them; mark unknowns explicitly.
