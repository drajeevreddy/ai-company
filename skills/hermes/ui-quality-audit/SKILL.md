---
name: ui-quality-audit
description: Use when auditing a web UI for measurable defects.
version: 1.0.0
author: hermes-curator
license: MIT
metadata.hermes.tags: [accessibility, contrast, ui, wcag, audit, playwright]
metadata.hermes.related_skills: [site-visual-review, app-security-slop-audit]
---

# UI quality audit

Measured, not eyeballed. Counts rendered defects — contrast, tap targets, accessible
names, alt text, heading structure — and turns them into an ordered fix plan.

Sibling skills, different classes — do not merge:
- **Subjective design quality** (hero, aesthetics, "which looks best") →
  `site-visual-review`.
- **Authz, injection sinks, CSP, secrets** → `app-security-slop-audit`.
- This skill: objective, countable defects in the rendered UI.

## When to Use

Load this when any of these is true:

- The user asks for an accessibility, contrast, or UI-bug audit of a site or app.
- The user says a page looks broken, washed out, or unreadable and you need to
  quantify it rather than guess.
- A design/theme change needs verifying across every theme and breakpoint.
- The user asks for "every bug listed" in a UI, or a fix plan for the interface.
- You are about to change a design token or theme utility and need to know every
  surface it affects.

Not this skill: judging whether a design is *good* (`site-visual-review`), or
auditing authz/injection/CSP (`app-security-slop-audit`).

## 1. Two passes, and they do different jobs

The **live browser pass finds** (what is actually broken, on which route, in which
theme). The **source read explains** (which component or token causes it). Do the
live pass first so the source read is targeted at a measured failure rather than a
suspicion — a source-only sweep produces a long list of theoretical problems and
misses the ones real users hit.

## 2. The measurement axes

Load every reachable route at desktop and mobile, and extract per page-load:

| Axis | What it records |
|---|---|
| `contrast` | computed colour vs resolved background, WCAG ratio, font size + weight |
| `tap` | every interactive element under 44x44 |
| `noname` | interactive elements with no accessible name |
| `imgalt` | images with no `alt` |
| `headings` | skipped heading levels |
| `h1count` | `<h1>` per page — 0 and >1 are both findings |

Emit JSON keyed by `<viewport>/<route>` so the whole run is re-analysable without
re-browsing. Screenshots are for the report; the JSON is the evidence.

Run the pass **once per theme**. See `references/accessibility-pass.md` for the
harness shape, the contrast maths, and the derived findings.

## 3. Aggregate per route before you report

The raw totals are close to useless on their own. Read the distribution:

- **A large count is usually one repeated pattern.** 305 sub-44px targets looked
  catastrophic; 125 sat on the landing page and the rest were the same 20px-tall
  navbar and footer link rendered on every page. One padding change was the
  highest-leverage fix in the entire audit. Report the leverage, not the count.
- **Clustering localises the cause.** Contrast failures on two or three routes while
  every other route is clean means a component or a token, not a global problem —
  and it tells you which files to open.
- **Clean axes are results.** `imgalt: 0` is evidence the pass ran and stops a later
  session re-testing it. Record zeroes explicitly.
- **A browser-side `:focus-visible` probe under-reports.** It does not synthesise
  keyboard focus, so missing focus rings do not show up. Treat focus as a source
  read and say so rather than reporting 0 as "no problem".

## 4. One-theme contrast failure → read the token layer first

When contrast breaks in exactly one theme, do **not** start editing components.
Read the token layer (`tailwind.config.js`, the CSS custom-property blocks) and look
for a utility rebound to a hardcoded literal.

The mechanism: a framework utility pinned globally to one theme's value makes every
call site of that utility invisible on the other theme. A case seen in practice —
`textColor.white: '#ECEDF0'` in the Tailwind config, where `#ECEDF0` *is* the dark
theme's text colour — turned 334 call sites into symptoms and the fix into one
config line. The first report said "334 hardcoded occurrences"; the truth was one
bug.

**Then check the tempting one-line fix.** Rebinding that utility to the theme
variable is wrong: it flips every use of it on a *deliberately coloured* surface
(buttons on brand colour, text on dark cards) to near-black. Before choosing,
count how many of the component's uses sit on a coloured background versus on the
page background, and change only the latter to the semantic token. Then split the
utility so the two meanings stop colliding — a future developer must not be able to
pick the wrong one by accident.

## 5. Be honest about coverage

Routes behind auth are unreachable from a logged-out live pass. A suspicion about a
gated page stays **SUSPECTED**; do not let it inherit the confidence of the pages
you actually measured. State which routes were not covered and why.

Same discipline for a finding you could not reproduce: if a static pass flags a
defect that the live pass contradicts on every page it *could* reach, say so and
downgrade it, rather than keeping the scarier version.

## 6. Deliverable: the prioritized fix plan

A count is not a deliverable. When the ask is "fix everything", produce a
self-contained plan a coding agent can execute with no prior context:

- **file:line for every change**, plus how to prove it landed. No line numbers = a
  wish list.
- **Priority order with a measured baseline and a target per metric**
  (before → target). "Do not regress N passing tests and a clean typecheck" is the
  most useful sentence in the document.
- **Carry the anti-fix.** Where a defect has a tempting one-line fix that is wrong,
  say so with its blast radius, or the next agent ships it confidently (see §4).
- **A "do not treat these as bugs" list** — the false positives already resolved
  (SPA catch-all answering 200, intentional empty states, third-party bot
  challenges). Otherwise the fixer re-opens settled questions.
- **The commands**, with correct working directories, and the rule that a backend
  edit is not live until it is deployed.
- **The canonical spec as its own section.** If the user hands you a spec of how
  their system works (type system, architecture), verify it against source and
  document the divergences — do not restate the spec as fact.

## Pitfalls

- **Exclude transparent text from contrast maths.** `rgba(0,0,0,0)` on a
  gradient-background-clipped display wordmark computes to a bogus ~1.0 ratio. Skip
  any colour with `alpha === 0`, and skip elements whose effective background is a
  `background-image` you cannot resolve, or the report fills with artefacts.
- **Set the theme before load, not after.** Write the theme storage key and
  `color-scheme` in an init script that runs before `goto`, or the first paint is the
  wrong theme and the measurement is garbage.
- **A themed utility and a literal utility are not the same thing.** When a design
  system has both a semantic token and a raw colour name overridden in config, grep
  for BOTH before concluding a component is broken.
- **Soft-404s hide missing pages.** A catch-all route or rewrite makes every unknown
  path return 200 with the shell, so a real 404 cannot be told from a typo. Verify by
  comparing the response body against `/` before reporting a page as present, and
  raise the missing-404 behaviour itself as a finding.
- **Confirm the fix in both themes at both viewports.** A change that looks right in
  dark is the exact bug you were fixing.

## References

- `references/accessibility-pass.md` — harness shape, WCAG contrast maths, axis
  extraction, and how each axis maps to a finding.
