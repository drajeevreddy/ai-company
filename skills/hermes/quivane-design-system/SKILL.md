---
name: quivane-design-system
description: Use when making any Quivane visual. Posts, web, image gen.
---

# Quivane design system

Load before any Quivane visual work: image generation, carousel or poster layout, web section,
slide. Full measurement lives at `Projects/Quivane-Design-System.md` in the brain vault.
Reference files: `/home/painarise/Pictures/INSPO` (six images, five Quivane).

Copy and numbers are governed by a different file — read
`/home/painarise/Music/Social Media Auto/quivane-brand-facts.md` before writing any text.
This skill governs **how it looks**, not what it claims.

## Tokens

- Ground `#FEFEFE` flat white. Ink `#000000`. Secondary gray `#6B6B6B`. Rules `#D9D9D9`.
- Accent red — flat `#D30000` in every INSPO asset. The logo-derived rule says `#E0010F` on
  `#FBF9F9`. Two reds are live; **ask which one before producing a set.** Never introduce a third.
- Outer margin ≈4.2–4.6% of width (≈46px at 1080). Top rail ≈3.1–3.8%.
- Grid: 8px. Canvas: 1080×1350 feed, 1080×1920 reel, 1254 square for standalone.

## Layout skeleton

1. Three-zone header rail: all-caps list left · centered red wordmark · all-caps list right.
2. Body band. Comparison pages are two equal columns split by one thin gray rule, badge centred
   on the rule; both sides run eyebrow → headline → subhead → list.
3. Payoff line, centred, after a horizontal rule.
4. Footer triad: values list left with a red bar, `quivane.in` centered, services list right with
   a red bar.

## Type

One neo-grotesque sans for the entire social system. Hierarchy from size, weight, case, colour —
never a second family. Headlines uppercase extra-bold, ~1.0em pitch, one red word maximum.
Labels and footer microcopy uppercase with wide tracking. Body sentence case, regular.
Stat numbers heavy and red.

Serif (GT Sectra / Newsreader) belongs to web display only. Do not put it in a social asset.

## Non-negotiables

- Red is scarce: logo, one emphasis word, CTA, positive icons, stat numbers, footer bars. Never a
  red background.
- Flat vector. No gradients, shadows, bevels, grain, rounded corners. A photoreal object render is
  allowed only as a metaphor (the chain), not as decoration.
- Photography is grayscale with at most one red subject.
- Argue by contrast: negative left / positive right, black vs red, minus vs check.
- Close every piece on a one-sentence payoff that restates the argument.
- Generous whitespace. Nothing crowds.

## Never ship in a generated asset

- **"Think. Build. Execute."** — retired 14 Sep 2026, but it is baked into most INSPO files.
  Do not replicate it from the reference.
- **Any statistic.** 40+/12+/98%, 10+/5+/100%, 100+ projects, 50+ businesses — all unsourced.
  No numbers about the agency appear in any asset, ever.
- A slogan of any kind. There is no replacement line.
- Technology or client names not verified in `quivane-brand-facts.md`.
- Emoji, hashtag stuffing, question-CTAs.

## Writing an image-gen prompt

State the tokens literally, then the structure, then the abstentions. Scaffold:

```
Flat vector brand poster, 1080x1350, pure white ground #FEFEFE.
Strict Swiss grid, outer margin 46px, thin #D9D9D9 hairlines.
Header rail: small uppercase letter-spaced black labels left, centered red wordmark.
Headline: ultra-bold uppercase neo-grotesque, tight leading, black, with the final word in
#D30000. One short red hairline under the kicker above it.
Body: sentence-case regular gray #6B6B6B.
Footer: two small uppercase lists with thin red vertical bars, centered wordmark line between them.
No gradients, no shadows, no rounded corners, no texture. No photography unless it is grayscale
with a single red subject. No statistics, no slogan, no emoji.
```

For a comparison piece, add: two equal columns, one vertical rule, circular outlined VS badge
centered on the rule, minus icons left and red check icons right.

## Checking the output

Sample the pixels, don't eyeball. A generated asset passes when the ground is `#FEFEFE`
(±3), the red is a single flat value, the outer margin is 4–5% of width, and there is no
second typeface. Pillow modal-colour count is enough:

```python
from PIL import Image; import collections
im = Image.open(path).convert('RGB')
print(collections.Counter(im.get_flattened_data()).most_common(6))
```

## Related

- `Award-Winning-Design.md` (vault System/) for web design audits.
- `Projects/Quivane-Social.md` for publishing state and what copy is frozen.
- `~/Downloads/ssc-0609/quivane-style.css` carries the live web navbar tokens
  (`--qv-red: #E30B13`, Inter / Inter Tight) — a third red, web scope only.
