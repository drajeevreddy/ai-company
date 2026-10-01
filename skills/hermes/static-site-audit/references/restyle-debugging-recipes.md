# Restyle debugging recipes (SSC Health session, 2026-09-06)

## Blank hero image, white heading on nothing
Cause: `.hero-section,...,.conferences-hero,...{background: transparent !important}`
overrode the inline `style="background: linear-gradient(...), url(...)"` on 5 pages.
Fix: drop the `!important` in BOTH `styles.css` and `styles.min.css` (pages load
the minified file — patching only the unminified one changes nothing live).
Inline backgrounds then win; video heroes without inline bg keep transparency.

## Giant empty gap = invisible content, not missing content
`.fade-in-up{opacity:0}` + `.fade-in-up.visible{opacity:1}` existed, but
`script.js` only ran `querySelectorAll('.fade-up')` through the observer —
33 blocks on 11 pages could never become visible. One-line fix: observe
`'.fade-up, .fade-in-up'`. Verify live: eval opacity + `visible` count after load.

## Mega-menu cards destroyed by theme override
First override used `.nav-links a` (12px uppercase inline-flex) — matched the
`.mega-card` anchors inside dropdowns too. Rewrite scoped everything to
`.nav-links > li > a`; dropdown internals untouched (verified: cards kept
original 16px style via computed font-size in browser eval).

## Blank icon tiles (orange boxes, no glyphs)
Font Awesome CDN never loaded in the user's browser (file:// + blocked
requests). Fix: self-host — download `all.min.css` + the 4 `webfonts/*.woff2`
from cdnjs into `assets/vendor/fontawesome/`, swap the `<link>` on all pages
(`../` prefix for nested dirs). Same for Google Fonts: fetch the css2 API with
a Chrome UA, keep only `/* latin */` @font-face blocks, download each woff2
into `assets/vendor/fonts/fonts.css` (watch out: naive URL-dedup can drop
faces — download per face unconditionally), strip the `@import` from the
shared stylesheets, link `fonts.css` locally. Confirm: grep for
`cdnjs|googleapis` returns only unrelated scripts; curl each vendor URL (200
+ sane byte size); browser eval shows `"Font Awesome 6 Free"` + non-empty
`::before` content on an icon.

## Proving "no links changed" across a bulk edit
Snapshot all `href=` values per file to JSON before editing; after editing,
assert every old href still present (additive `<link>`/`<script>` tags only).

## Full icon audit (names + prefixes + live render)
Extract every `<i class="fas|far|fab ...">` across HTML+PHP; split style
prefix from icon names; exclude utils (`fa-fw`, sizes `fa-Nx` — those are
not broken icons). Name check: each must match
`\.fa-([a-z0-9-]+)::?before` in the loaded `all.min.css` (FA5 aliases like
`fa-file-medical-alt` live in the v4compatibility block). Prefix check:
fas/far/fab must match the icon's style — a solid-only icon under `far`
renders blank. Live proof: create each icon in the browser and read
`::before` content + bounding width; `none`/empty/0-width = broken.
(A 53-icon site audited 53/53 this way.)

## Inline-SVG fallback for font-proof icons
When tiles must render with zero font dependency: download per-icon SVGs
from `raw.githubusercontent.com/FortAwesome/Font-Awesome/<ver>/svgs/solid/<name>.svg`
(alias names 404 — use the canonical file, e.g. `file-waveform.svg` for the
`fa-file-medical-alt` alias). Scripted replace of `<i class="fas NAME">`
with `<svg class="fas NAME" viewBox=...><path/></svg>` preserving classes;
add sizing CSS (`.tile svg{width:24px;height:24px;fill:currentColor}`).
Verify: replacement count + computed fill/size live.

## Dropdown stuck permanently open
Panel visible on load with no hover = suspect `display:flex !important`
beating the base `display:none`. Before "fixing", prove original behavior:
serve the pristine baseline and eval computed display with no hover (one
mega panel measured `flex`, 476–1376px in a 1280px viewport — originally
always open AND off-screen). Fix: gate on hover with higher-specificity
`!important` rules, re-anchor to the navbar center, cap width at
`min(880px, calc(100vw - 48px))`; verify closed-on-load (`none`) plus
open-state rect fits the viewport.
