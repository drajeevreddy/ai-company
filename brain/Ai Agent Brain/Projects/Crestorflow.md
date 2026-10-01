# Crestorflow

The owner's AI-native career/learning platform — Discovery agent, roadmap generation, Learn artifacts, squad features, verification. Treated as a commercial product, not a side project.

## Where things live

| What | Path |
|---|---|
| Repo | `/home/painarise/crestorflow-ai/` |
| Audit workspace (all evidence) | `/home/painarise/crestorflow-audit/` |
| Audit report (62 findings) | `.../Crestorflow-Audit-Report.{md,pdf}` |
| Master fix prompt | `.../Crestorflow-Master-Fix-Prompt.{md,pdf}` |
| Handover doc (owner-written) | `.../crestorflow-ai/docs/HERMES-CONTEXT.md` |
| pentest-ai MCP report | `~/reports/pentest-41b6f389-*.{md,html,pdf}` |

## Stack and live infrastructure, verified

| Layer | Reality |
|---|---|
| Frontend | React 18 + TS + Vite + Tailwind + wouter + Clerk, in `frontend/` |
| Backend | Convex `aromatic-toad-460` — 123 modules, 140 functions, **85 public** |
| Host | CloudFront `E35XQXECT0KBDW` → private S3, OAC, TLS1.2_2021 |
| CSP enforced by | `infra/lib/site-stack.ts` — **not** `public/_headers` (AWS ignores it) |
| Auth | Clerk, issuer `clerk.crestorflow.com` |
| Deploy | GitHub Actions → OIDC role pinned to `repo:abdul-malik006/crestorflow-ai:ref:refs/heads/main` |
| Tests | Vitest — 115 passed / 1 skipped (116 files), **2774 tests** |

The handover doc claims "~1,246 tests". The real figure is 2,776. Handover docs drift; run the suite.

## The audit — 62 findings, all verified before reporting

**Verdict: the backend is sound.** No auth bypass, no cross-tenant leak, no fail-open gate across all 85 public Convex functions — every one was read by hand, and unauthenticated calls against live production were all correctly refused. Typecheck clean, 2,774 tests pass, 0 console errors across 19 routes.

| Severity | Security | UI | Total |
|---|---|---|---|
| HIGH | 1 | 4 | **5** |
| MEDIUM | 8 | 12 | **20** |
| LOW | 9 | 14 | **23** |
| INFO | 8 | 6 | **14** |

The five HIGH, and what each actually is:

- **H1** — `/board` and `/onboarding` headings are invisible in the default light theme, **1.08:1**. Root cause is one line in `tailwind.config.js`: `textColor.white` is pinned to `#ECEDF0`, which *is* the dark theme's value, applied theme-blind. The tempting one-line fix (rebind to `var(--color-text-main)`) is wrong — it turns every `text-white` on a coloured surface black-on-blue, including three CTAs on `/board` itself. Fix 5 of 13 hits on `/board`, 1 on `/onboarding`. See [[Skills/audit-false-positives]] for why the naive fix is a trap.
- **H5** — `verification.verify` double-bills on concurrent calls: the guard reads before the model call and writes after, the idempotency key is a fresh `crypto.randomUUID()` each time, and the burst limiter is capacity 2/min by design.
- **H2** — the markdown sanitizer allows `target` without forcing `rel`. Narrow: the app's own link renderers (`lib/discovery/citations.ts`) already emit `rel="noopener noreferrer"` with tests. Only the `DiscoverPage` sanitizer is exposed.
- **H3** — `object-cover` crops the founder portrait (cuts the subject), a user's own project cover, and users' bug-report screenshots. Against the standing "whole image, optically centred" rule.
- **H4** — contrast failures in *both* themes: purple `Log In` 3.62:1, `text-gray-500` empty states, 10px footer labels, and `--color-brand-blue` at 10–11px on dark (3.21–3.52:1 — systematic, one token fix).

**The biggest UI sweep:** 305 sub-44px tap targets across 24 page-loads. 125 on `/` alone, and every marketing/legal page carries 9–13 because the 20px-tall navbar+footer link pattern repeats. One padding change clears most of them.

**Four spend paths reach the model with no budget guard** (M1–M4) and **the SSRF guard has two proven gaps** (IPv6 `::/96` escapes both blocklists; the response body is read outside the 8s timeout). Cost surface is the attack surface on this product — that class is the highest-value thing found.

## The pentest-ai MCP was 93% false positive here

All 15 "medium vulnerabilities" are the SPA catch-all — `/debug`, `/admin`, `/.env`, `/git/config` all return the byte-identical shell. Its single "attack chain" is four 403 hits chained together, and 403 means *denied*, not exposed. Verified by oracle: 0.

Every real finding came from reading source. Stand up the tool, then treat its report as a lead generator, never as the assessment. Full catalogue in [[Skills/audit-false-positives]].

## The typography system — spec vs what ships

Documented as SF Pro (sans) + JetBrains Mono (mono). Verified reality differs in three ways:

- `font-sans` and `font-display` are **byte-identical**, and both start at `Geist` (loaded from `fonts.bunny.net`) — the SF stack is only the fallback. Two names, no hierarchy.
- `font-mono` lists **JetBrains Mono second, and it is never loaded** — no `@font-face`, no webfont link, no preload. Dead weight in the chain. `Geist Mono` isn't loaded either.
- Two different sans definitions exist: `index.css:92` has Geist, `index.html:38` doesn't.

Usage reality: `font-mono` 113, `font-sans` 18, `font-display` 18 — mono is the dominant family, six times the body font.

## Open with the owner

- **No code has been changed.** The audit is read-only; the repo is untouched. The fix pass is specced and not started.
- Which of the two "stale" repo files to keep — `skills-manifest.md` / `skills-reference.md` describe the old ~150-skill set and now contradict the pushed `SKILLS-INDEX.md`.
- Whether to work the fix list in severity order, and whether H1 ships alone first (it is user-visible to every light-mode visitor today).
- The cron `crestorflow-audit-morning-digest` fires 07:49 IST to Telegram; decide keep-as-regression-check or remove.

See also: [[Skills/audit-false-positives]] · [[Skills/verify-by-running-it]] · [[System/Code-Quality-Bar]]
