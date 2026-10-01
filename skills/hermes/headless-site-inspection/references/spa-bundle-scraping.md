# Scraping JS SPAs via Bundle Analysis + Backend Discovery

Validated 2026-09-04 against a Vite React SPA (x402-kit on Vercel) where
web_extract was blocked and curl of routes returned only index.html.

## When to use this instead of Playwright/rendering

- Route HTML is an empty shell (`<div id="root">` + one
  `/static/js/main.<hash>.js` script tag). Content loads client-side.
- Spinning up a full browser is slow or the browser server is down.
- You suspect a decoupled backend API (FastAPI/Express on another host).

## Procedure

1. `curl -sL <site>/` → confirm SPA shell, extract the JS bundle URL
   (`/static/js/main.<hash>.js`). Save bundle to /tmp.
2. Regex the bundle for app-level facts (skip minified lib noise):
   - routes: `/(dashboard|playground|agent|docs|api)[A-Za-z0-9/_-]*`
   - backend hosts: `https://[a-z0-9.-]+\.(vercel\.app|onrender\.com|fly\.dev|railway\.app)`
   - embedded copy: string literals 25+ chars filtered against code markers
     (`function(`, `=>`, `props.`, `{}`). First pass WILL be mostly library
     noise — filter aggressively, then grep for domain keywords.
   - config arrays: scorecards, policies, nav labels (e.g. `JO=[...]`).
3. Probe the backend directly with curl. Guessing ladder:
   `/openapi.json` (FastAPI self-documents) → `/docs` (Swagger UI confirms
   FastAPI) → `/api/<resource>/tree`, `/health`, obvious REST paths from
   bundle strings. In the validated case the backend exposed
   `GET /api/docs/tree` (file listing) and
   `GET /api/docs/content?path=<file>` (full markdown) — 25 docs, zero rendering.
4. Prefer backend endpoints over rendered pages from here on: faster,
   complete, no JS needed.

## Camofox server recovery

If browser tools fail with `Cannot connect to Camofox at
http://localhost:9377`, the server process is down — start it detached:
`camofox server start --port 9377` in background (returns immediately,
server keeps running). Verify with a fresh browser_navigate before
assuming browser inspection is unavailable. Do NOT record 'browser is
broken' as a durable fact; it is setup state.
