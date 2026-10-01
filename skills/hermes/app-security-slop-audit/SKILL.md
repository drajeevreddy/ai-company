---
name: app-security-slop-audit
description: Audit an owned codebase for authz holes and AI slop.
metadata.hermes.tags: [security, code-audit, authz, csp, ai-slop]
---

# App security + slop audit

White-box audit of a codebase the user owns. Ordered by value: authz first, then
injection sinks, then headers, then integrity/fabricated content, then prose.

## 1. Authz matrix scan before reading files

Do not hand-read 80 handlers. Write a scanner, but **discover the helper names
first** — assuming `requireUser` is the only gate produces a false-positive
avalanche and a wrong report.

```python
# pass 1: every auth-ish helper actually defined in the repo
helpers |= set(re.findall(r'(?:async\s+)?function\s+([a-zA-Z]*[Rr]equire\w+)', src))
# pass 2: for each exported handler, does its body call one of them,
# or read ctx.auth.getUserIdentity() directly?
```

Brace-match each `export const X = (query|mutation|action)({...})` body, then test
`\bhelper\s*\(` inside it. Report only functions with **no** gate and **no**
direct identity read. Then read that short list by hand.

Convex specifics worth knowing:
- Actions cannot use `ctx.db`; they delegate to internal mutations. A wrapper with
  no gate is fine **if** the internal it calls does `requireUser` and scopes every
  read to `user._id`. Verify that internal — do not infer it.
- A private helper called by a public mutation counts as a gate (e.g.
  `setProgressFlag` doing `requireUser` + `requireOwnedRoadmap`).
- Cross-tenant leaks hide in unscoped index reads: `.withIndex('by_x').first()`
  with no `userId` equality. This is the single most common real finding.
- A public query whose args include another user's id (`ownerId`, `userId`) is a
  candidate even when a `requireMembership(groupId)` gate exists — check that the
  other id is validated against the group, not trusted.

## 2. Injection sinks

`grep -n 'dangerouslySetInnerHTML'`. For each hit, check the producer: markdown
renderers are the classic case because **marked does not sanitize** (removed in
v5; docs tell you to use DOMPurify). No sanitizer dependency + no CSP = live XSS
on model output.

Fix without adding a dependency: an allowlist sanitizer at the final sink, using
`DOMParser` in the browser. Apply it **after** your own markup rewrites so the
injected markup is validated too — that also re-escapes attribute values your
rewrite only quote-escaped. Unwrap unknown elements (keep their text) instead of
deleting; return `''` if `DOMParser` is undefined (fail safe).

## 3. Verify CSP against the real build, never by eye

A CSP guess breaks production auth. Two checks that are deterministic:

1. Hash the inline scripts in **dist/index.html** (not the source index.html —
   Vite rewrites it) and confirm they match the `sha256-` values you put in CSP.
   `re.findall(r'<script>(.*?)</script>', html, re.S)` then sha256+base64.
2. Serve `dist/` with the exact headers from your deploy config and load it in a
   browser. Prove the directives landed from page state, not from a screenshot:
   - inline script ran: `document.documentElement.getAttribute('data-theme')`
   - inline style applied: a computed style set by index.html's `<style>`
   - external stylesheet allowed: `[...document.styleSheets].map(s=>s.href)`
   - resolve the **real** font/img origins from the fetched CSS
     (`curl` the Google Fonts CSS and read the host out of it) rather than
     assuming.

Env header order: enforce the headers that cannot break anything (nosniff,
frame-options, referrer-policy, permissions-policy, HSTS) and hash-pin
`script-src`. Always state which parts still need a preview smoke test (Clerk and
similar inject scripts at runtime) and give the one-block revert.

## 4. Fail-closed service auth

Grep for `if not <secret>:` followed by `return True`. An empty shared secret
must refuse every request (503), not authorize. Use
`secrets.compare_digest`, never `==`. When the service is a mock that fabricates
content, also check whether it claims grounding it does not perform: send the
same request with unrelated sources and diff the payload.

Four invariants to add to the service's own test file:
- unset secret -> 503 (fail closed), missing/wrong token -> 401, correct -> 200
- `/docs`, `/redoc`, `/openapi.json` -> 404 unless explicitly opted in via env
- `/health` reports nothing about the credentialed session it fronts
- bind host defaults to loopback, overridable by env

Also check the bind address (`host="0.0.0.0"`) and update the service's own tests
to assert the refusal — a fix without a test regresses silently.

## 5. Integrity findings count as findings

Fabricated content is a trust finding, not a copy nit: hardcoded "grounded"
analysis, invented uptime figures, fake telemetry shown to users ("Ran 3
searches"), stock photos of real strangers as testimonials. Look for `setTimeout`
standing in for a real POST — a form that reports success and discards the data.

## 6. Slop audit: build the ban list, then kill the false positives

Load the ban list from a dedicated skill if one exists; otherwise use the tiered
vocabulary (Tier 1 always-flag / Tier 2 cluster / Tier 3 density).

**The critical step is the second pass.** A raw word scan over a real codebase
returns mostly noise:
- Domain terms (`showcase`, `navigate`, `harness`, `load-bearing`) are correct
  vocabulary. Substituting them breaks code for nothing.
- A ban list *document* naming the banned words is not an instance of slop.
- Test fixtures are data, not prose.
- Substring matches lie: `LearningStep` matched "learnings".

Filter to genuine uses, print `file:line  [word]  <the line>`, and read the list
before editing. Then fix in this priority: user-facing copy > generated/fabricated
content > comments > docs.

Never rewrite prose inside a structured format you cannot re-verify. After edits,
**re-run the full test suite and typecheck** — copy often lives in fixtures the
tests assert on. Grep each string you intend to change for test references first.

## 7. Cruft sweep (do this last)

Look for evidence of an abandoned previous stack living beside the current one:
unusual root dirs (`models/`, `pages/`, `supabase/`, `store/`, `tests/`) and
`fix_*.cjs` / `update_*.cjs` / `replace.js` throwaway codemods. Verify each is
unreferenced (grep the basename across ts/tsx/js/json/md, excluding the file
itself) before deleting.

Specifically hunt `// @ts-nocheck`. One directive can hide the whole typecheck:
remove it, read the real errors, fix them, and only then claim the typecheck is
clean.

## 8. Driving the pentest-ai MCP

Exposed as `mcp__pentest_ai__*` (start_engagement, builtin_scan, run_recon,
test_web_app / _api_security / _credentials / _vulnerabilities, http_request,
validate_finding, generate_report). `tool_call` accepts only ONE of these per
call — unlike connector tools they are not batchable, so issue them as separate
tool_call invocations in one turn.

**Stand up the vulnerable baseline from git.** Before scanning the fixed tree,
run `git show HEAD:<path> > /tmp/.../main.py` and serve it on its own port. This
does two things: it gives the scanner a real vulnerability instead of an
assertion that it would have found one, and it yields a before/after finding
count on an identical target.

**Do not treat the finding list as the assessment.** Measured on a local target:
- The fail-open auth bypass (`POST /artifact` -> 200 unauthenticated) appeared in
  **zero** of 27 automated findings. The generic unauth-REST heuristic flagged
  `GET /health` as HIGH instead and never touched the open write endpoint one
  path away. Use `http_request` to drive the real PoC by hand; it returns a
  hashed evidence artifact per call, which is the citable proof.
- What the automated pass *did* get that a source read missed: FastAPI serves
  `/docs`, `/redoc` and `/openapi.json` by default. Schema disclosure on a
  credential-holding service. Scan the target even when you have read the code.

**Quantify noise before reporting counts.** A 582-finding run was 562
`secrets-patterns-pii` hits: `hex_colors` matching the app's own brand palette
(`["#0055FF","#ffffff"]`) and `email_3` matching footer text, both on WordPress
paths that do not exist. Group by template family and severity first; report the
handful that survive.

**An SPA catch-all rewrite manufactures false positives.** With `/(.*) ->
/index.html`, every path returns 200 + the app shell, so the path-probe
heuristic reports `/admin`, `/debug`, `/actuator`, `/metrics`, `/_admin` as
reachable. Verify by checking whether the evidence body is the shell HTML; if so
it is not a finding — but the catch-all itself is worth raising, since the app
cannot distinguish a real route from a 404.

Other behaviour to expect:
- A URL target makes the port scanner scan the **host**: "open 22/tcp, 3389/tcp"
  are the machine's services, not the app's.
- `builtin_scan` runs standalone and returns `engagement_id: ""` — it does not
  attach to an engagement.
- "Missing X-XSS-Protection" is outdated advice; the header is deprecated in
  favour of CSP. Do not add it.
- Findings default to `verdict: candidate`. The generated report states
  "Verified by oracle: N" — read that line before repeating a severity.
- Reports land in `~/reports/pentest-<engagement>-<date>.{md,html,pdf}`.

## Reconcile delegated workstreams against the report

Fanning the audit out to parallel subagents is right for coverage but wrong as a
finish line. When their summaries land, **diff their finding list against the
report item-by-item** — do not assume that reading their files once captured
everything. Two failure modes seen in practice:

- **A dropped finding.** One workstream reported a genuine MEDIUM (two entry
  points claiming the same row under different cache keys) that never made it
  into the numbered report, because it was read while skimming for the
  higher-severity items above it. Diff by count and by topic, not by memory.
- **A severity you under-called.** The same workstream rated a confirmed
  double-billing HIGH while the report had it MEDIUM. Re-read the child's
  reasoning; if the impact class is the one the threat model names as primary,
  the child is often right and the first pass was conservative.

Children also over-claim in the other direction. In the same batch one asserted a
build file was "publicly readable at /_headers" — a live probe showed the SPA
rewrite answering that path with the shell, so the finding was source hygiene,
not exposure. **Every externally-visible claim a child makes (a URL is reachable,
a file is exposed, an endpoint answers) must be re-probed yourself** before it
enters the report. Claims about source are cheaper to check and usually sound;
claims about live behaviour are where they drift.

## Pitfalls

- `pkill -f <pattern>` kills the shell running it when the pattern appears in its
  own command line. Use `pgrep -af "patt[e]rn"` (bracket trick) or kill by pid.
- An SPA `rewrites` rule also swallows `/api/*`; a Next-style API route in a Vite
  app is dead code that still reads like a live surface.
- Report a blocker instead of inventing output. If a browser console API is
  unavailable, prove behaviour from page state instead of claiming you saw logs.
- **The SPA catch-all answers 200 for any path without a known file extension** —
  including `/.env` and `/.git/config`, not just `/debug` and `/admin`. Before
  believing any "path reachable" finding, `md5sum` the response against `/`.
  Missing assets that *do* carry a known extension correctly 403 from S3, and the
  403 body is byte-identical for a missing file and a forbidden one, so there is no
  enumeration oracle either way.
- **A public function gated by a private helper reads as ungated to a scanner.**
  Sweep for `^export const X = (query|mutation|action)({`, brace-match the body, and
  flag functions with no exported-helper call and no direct
  `ctx.auth.getUserIdentity()` — then read every flagged body by hand before
  reporting. `setProgressFlag` and `requireOpenPart`-style private gates resolve
  most of the list. A public `action` with no inline gate is fine if the internal it
  calls re-derives the caller; verify that internal, do not infer it.
- **Test UI contrast in BOTH themes.** A theme toggle means a hardcoded
  `text-white` is invisible under light mode *only*, and one toggle click hides it.
  Set the theme storage key in `localStorage` (and `color-scheme`) in
  `add_init_script` before load, then measure per theme. A page that renders
  correctly in dark and washes out in light reads as "designed dark" to a reviewer
  who only looked once.
- **Exclude transparent text from contrast maths.** `rgba(0,0,0,0)` on a gradient
  background-clipped display wordmark computes to a bogus ~1.0 ratio. Skip any
  colour with `alpha === 0`, and skip any element whose effective background is a
  `background-image` you cannot resolve — otherwise the report fills with artefacts.
- **Run the project's own suite and typecheck.** Cheap on a large codebase and it
  both bounds the real defect surface and validates the handover doc: test counts
  drift (one doc claimed ~1,246 `it()` blocks where the suite actually ran 2,776).

## Convex deployment probing

- Registered HTTP routes live on `<deployment>.convex.site`; `<deployment>.convex.cloud`
  is the RPC endpoint. A `/health` probe against `.cloud` 404s by design — do not
  report the route as missing.
- Function reachability is testable unauthenticated over HTTP:
  `POST <deployment>.convex.cloud/api/query` with
  `{"path":"module:fn","args":{},"format":"json"}`. A correct deployment answers
  `{"status":"error","errorMessage":"[Request ID: …] Server Error"}`; the generic
  message is Convex redacting the thrown error, so it proves fail-closed without
  leaking internals. Probe a query, a mutation, and a legitimately-public query
  (one that should return data) to prove the difference.
