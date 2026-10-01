# Quivane — design system

Measured 15 Sep 2026 off the six files in `/home/painarise/Pictures/INSPO`. Pixel-sampled,
not eyeballed. Five files are Quivane; one is a different brand (see the end).

This file is the **visual** language. `Quivane-Social.md` and
`/home/painarise/Music/Social Media Auto/quivane-brand-facts.md` still govern **copy and numbers.**

## The set

| File | Size | What it is |
|---|---|---|
| `9aef8fba-…jpeg` | 1254×1254 | Capability sheet — 40+/12+/98% metrics band, dotted world map, industry list |
| `506B5CBD-…jpeg` | 1254×1254 | AI DEMO vs AI IN PRODUCTION comparison, VS badge, check/minus icons |
| `25641E27-…jpeg` | 1254×1254 | DISCONNECTED TEAMS vs CONNECTED EXECUTION, broken vs intact chain render |
| `122EB78F-…jpeg` | 1092×1440 | Portrait poster — huge headline over a grayscale summit photo, red jacket |
| `8ecfca11-…jpeg` | 1092×1440 | Portrait poster — asymmetric two-column, headline left, concrete architecture right |
| `525242792_…jpg` | 150×150 | **adory creatives** logo, monochrome, unrelated to Quivane |

## Palette (sampled)

- **Ground `#FEFEFE`** — flat white on all five Quivane files.
- **Accent red, flat value ≈ `#D30000`.** Sampled reds cluster `#D00101`–`#D3010A`; the spread is
  JPEG jitter on a flat fill.
- **Ink `#000000`** — pure black, not `#0A0A0B`.
- **Secondary gray ≈ `#6B6B6B`**, rules and dividers `#D9D9D9`.
- **adory only:** ground `#F2F1EF`, mark `#000000`, no accent.

**Open with the owner:** two accent reds now live in the wild. The logo-derived rule says
`#E0010F` on `#FBF9F9`; every one of these assets is `≈#D30000` on `#FEFEFE`. Same family,
~5% darker and 1% warmer. Pick one and write it down; don't let both ship.

## Layout

- Canvas: 1254 square and 1092×1440 portrait in this set; 1080×1350 feed and 1080×1920 reel
  are the publishing targets.
- **Outer margin ≈4.2–4.6% of width** — about 46px at 1080. Top rail ≈3.1–3.8%.
  This is **tighter than the published carousel** (measured now: 129px left, 55px top on
  `quivane_instagram_*_full_logo.png`). The INSPO grid is the newer, denser one.
- **Header is always a three-zone rail:** all-caps list left, centered red wordmark, all-caps
  list right.
- **Footer is always a triad:** values list left with a red vertical bar, `quivane.in` centered,
  services list right with a red vertical bar.
- Comparison pages: two equal columns, one thin vertical rule, badge centred on the rule.
- Rules organise, they never decorate: 1px gray `#D9D9D9` between columns and bands, short red
  hairlines only under kickers and beside footer blocks.
- Portrait posters run the photograph full-bleed — content bbox touches the right and bottom
  edges (measured 0% margin).

## Type

- **One neo-grotesque sans family for the whole social system.** Hierarchy comes from size,
  weight, case and colour — never from a second typeface.
- Display headlines: uppercase, extra-bold/black, tight leading, ~1.0em line pitch.
- Labels, eyebrows, nav lists, footer microcopy: uppercase, small, wide letter-spacing.
- Body, subheads, list items: sentence case, regular weight.
- Key word swaps to red inside a black headline. Only one red word per headline.
- Stat numbers: heavy, red, with a small gray label under them.
- **Serif does not appear here.** `quivane-brand-facts.md` sets GT Sectra / Newsreader for web
  display and Inter for UI; the social set is sans-only. Keep those two scopes apart.

## Rules, distilled

1. **Red is scarce.** Logo, one emphasis word, CTA, positive icons, stat numbers, footer bars.
   Nothing else. It never fills a background.
2. **Flat vector only.** No gradients, no shadows, no bevels, no grain, no rounded corners.
   The one 3D element permitted is a photoreal object render used as metaphor (the chain).
3. **Photography is grayscale** with at most one red subject or one red overlay rule.
4. **Argue by contrast.** Left negative / right positive, black vs red, minus vs check,
   broken vs whole. Mirrored columns, same eyebrow → headline → subhead → list structure both
   sides.
5. **Always close on a payoff line** that restates the argument in one sentence
   ("The difference is execution.", "End-to-end isn't a service. It's the difference.",
   "Ideas deserve execution.").
6. **Grid discipline:** narrative left-aligned, metadata right-aligned, the payoff centred.
7. **Whitespace is the premium signal.** Nothing crowds; margins are generous at the band level
   even though the outer margin is tight.
8. **Repeat the vocabulary.** *ideas, strategy, execution, real, progress, tomorrow* recur in
   headline, column, footer and overlay on the same page.

## What in this set must not ship

The INSPO set is the visual language. It is not cleared copy.

- **"Think. Build. Execute."** is on nearly every asset here. Retired 14 Sep 2026 for social.
- **40+ products / 12+ industries / 98% retention** and **10+ / 5+ / 100%** appear here.
  Unsourced. Do not ship either set.
- **"Why 7-day tracking."** in the top rail of `506B5CBD`: this is not a design-system rule.
  It looks like an annotated screenshot or an internal file. Confirm with the owner before
  treating that rail as canonical.
- Anything drawn from these files that names a technology or a client: verify against
  `quivane-brand-facts.md` first.

## adory creatives

A separate identity, do not blend it into Quivane.

- Lockup: `Ad` monogram — clapperboard arm built onto the `A`, microphone cut out of the `d` bowl —
  above the lowercase wordmark `adory creatives`.
- Monochrome: `#000000` on `#F2F1EF`. No accent colour at all.
- Mark is ultra-bold geometric sans; wordmark is a transitional serif, all lowercase, about
  30% of the mark's height.
- Flat vector, strong silhouette, readable at 150×150 (it ships as a profile picture at that size).
