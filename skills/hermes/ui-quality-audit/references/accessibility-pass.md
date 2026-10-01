# Accessibility pass — harness shape and derived findings

Depth for §2 of SKILL.md. The pass is a single Playwright script that visits every
reachable route at more than one viewport, per theme, and writes one JSON blob.

## Run shape

```
for theme in (light, dark):
  for viewport in (1440x900, 390x844):
    for route in routes:
      context with init script that sets the theme BEFORE load
      goto(route, wait_until="domcontentloaded")   # NOT networkidle
      evaluate(extract_all_axes)  -> record under f"{viewport}/{route}"
      screenshot
```

Two operational notes that cost real time if missed:

- **`wait_until="networkidle"` hangs.** Third-party auth widgets and long-poll
  connections never go idle, so a route with an embedded sign-in iframe can sit for
  45s and blow the whole run. Use `domcontentloaded` and add a short explicit wait.
- **Dump JSON incrementally**, or a timeout on route 18 of 19 loses everything.
  Write after each route, and support a `--only <route>` flag so a single page can
  be re-measured without a full sweep.

## Setting the theme before load

The measurement is worthless unless the first paint is the right theme. In an init
script (runs before any page JS):

```js
localStorage.setItem(THEME_KEY, theme);      // discover the real key from source
localStorage.setItem('color-scheme', theme);
document.documentElement.setAttribute('data-theme', theme);
```

Find `THEME_KEY` in the app's theme provider or the inline `index.html` script; do
not guess it. Also set the class if the CSS scopes on `.light` / `.dark` rather than
the data attribute.

## Axis extraction

Run one `page.evaluate` returning all axes so the DOM is walked once.

**`contrast`** — for every element with visible text:

1. `getComputedStyle` for `color`, `fontSize`, `fontWeight`.
2. Walk ancestors until you find a non-transparent `background-color`. If none is
   found, fall back to the document body background.
3. Compute the WCAG ratio:

```js
const lum = (rgb) => {
  const c = rgb.map(v => { v /= 255; return v <= 0.03928 ? v/12.92 : Math.pow((v+0.055)/1.055, 2.4); });
  return 0.2126*c[0] + 0.7152*c[1] + 0.0722*c[2];
};
const ratio = (a, b) => {
  const [l1, l2] = [lum(a), lum(b)].sort((x, y) => y - x);
  return (l1 + 0.05) / (l2 + 0.05);
};
```

4. Threshold: **4.5:1** normal text; **3:1** for large (>=24px, or >=18.66px when
   bold). Record the size and weight alongside the ratio so the threshold can be
   re-derived later instead of trusted.

**Skip these or the report fills with artefacts:** any colour with `alpha === 0`
(gradient-clipped wordmarks), any element whose effective background is a
`background-image` you cannot resolve, and zero-size or `display:none` elements.

**`tap`** — every `a, button, input, select, textarea, [role=button], [onclick]`
whose bounding box is under 44x44. Record width, height and a selector.

**`noname`** — interactive elements with no accessible name: no `aria-label`, no
`aria-labelledby` resolving to text, no `title`, no visible text content, no
associated `<label>`.

**`imgalt`** — `img` without an `alt` attribute (an empty `alt` is valid and means
decorative — do not flag it).

**`headings`** — the document's heading sequence; flag skips (h1 -> h3).

**`h1count`** — a number. `0` (missing) and `> 1` (multiple) are both findings, and
both are common.

## How each axis maps to a finding

| Axis | Finding shape | Notes |
|---|---|---|
| `contrast` | per-element, with ratio + location | cluster by route first (SKILL.md §3) |
| `tap` | aggregate count + the repeated component | usually one pattern, see below |
| `noname` | per-element, name the icon | the live pass only sees rendered surfaces; a static pass finds more (modals, auth pages) |
| `imgalt` | per-element | often genuinely 0 — record it |
| `headings` | per-route skip list | low severity, cheap to fix |
| `h1count` | per-route | 0 on marketing pages is common; >1 usually means a banner component also emits h1 |

## Reading the tap-target distribution

This is the axis where the total most misleads. Group the hits by *component or
route shape*, not by element, and look for the shared pattern:

- If the same navbar/footer link is under-height on every page, the count scales
  with page count while the fix is one rule. Say "one padding change clears N of
  them" rather than "N failures".
- If hits are concentrated on one route, that route has a bespoke component — fix it
  there.

Report both numbers (total and post-fix estimate) so the reader understands the
leverage.

## Cross-checks worth running in the same session

- **Routing contract probes.** Fetch a handful of paths and compare the response
  body against `/`. Byte-identical body = soft-404 = the route does not exist. Also
  probe a missing asset with a real file extension — if the host is an object store
  behind a rewrite, that should 403 rather than serve the shell, which confirms the
  rewrite is extension-aware.
- **Console capture.** Collect `console` messages, `pageerror`, and failed requests
  per route. Zero errors across every route is itself a reportable result.
- **The project's own suite.** Run the typecheck and test suite; it bounds the real
  defect surface and validates any handover doc, whose test counts are frequently
  stale.

## Deciding what is NOT a finding

Check these before writing them up — each one looks like a bug and is not:

- A designed empty state for a resource that legitimately has no rows.
- A third-party bot challenge (page title becomes "Just a moment...") on a
  subdomain the app does not control.
- A transparent gradient-clipped display wordmark at a bogus ~1.0 ratio.
- Console noise originating from a third-party widget rather than app code — check
  the message's source before attributing it.
