# Award-Winning Design

Distilled from `design-review` (audit → fix → verify loop) and the design-system skills. Full reference: `skill_view('design-review')`. Companion build skills: `design-consultation`, `design-html`, `popular-web-designs`, `claude-design`.

## The loop (never audit without fixing)
1. Baseline: first impression + extract the actual system (fonts, palette, heading hierarchy, spacing scale, touch targets).
2. Page-by-page audit against the checklist below. Score it.
3. Triage by visual impact. Fix in source, one atomic commit per fix.
4. Re-verify after every fix (before/after screenshots where the harness allows; otherwise verify via DOM/logs/user).
5. Final pass for cross-page consistency. Record learnings.

## Audit checklist (10 categories)
- Hierarchy: one clear primary action per view; headings in logical order; billboard test (5-second glance = what/where-next).
- Spacing: consistent scale (4/8pt), related items grouped, no orphaned whitespace, vertical rhythm holds across breakpoints.
- Typography: max two families, fluid sizes, line-length 45–75 chars, no Title Case headings, no gray-on-gray body text.
- Color: palette extracted and counted (drift = new hexes); contrast meets AA; one accent used sparingly.
- Components: buttons/inputs/cards share radius, border, shadow language; empty/loading/error states designed, not blank.
- Navigation: wayfinding — user always knows where they are and how to go back; mobile nav reachable one-handed.
- Touch targets: minimum 44px; no overlapping tap areas.
- Motion: transitions under 300ms, one easing language, no layout-shift jank; reduced-motion respected.
- Performance: no render-blocking hero assets, images sized, no invisible slow interactions draining the goodwill reservoir.
- AI-slop visuals: generic purple gradients, identical card grids, emoji icons, lorem-ish placeholder copy, stock-photo hero with no product in it.

## Hard rules
- Real copy, never lorem. Real data in mockups, never 3 identical cards.
- Fix the system (token/component), not the instance — one-off overrides are how drift starts.
- Consistency across pages outranks perfection on one page.
- Match structure to the repo: extract tokens before inventing new ones.
