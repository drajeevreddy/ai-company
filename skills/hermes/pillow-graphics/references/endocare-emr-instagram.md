# Worked example: EndoCare EMR Instagram campaign (4 posts, 4:5)

Session context (Aug 2026): user is building an on-premise clinic EMR under the
existing EndoCare brand (same brand as the doccare/EndoCare clinic app). Selling
point: "EMR hosted on the clinic's own machine" — removes third-party data-
management risk. User chose the existing EndoCare brand (asked via clarify; the
alternative options offered were generic 'EMR' or a new product name).

## Deliverables

Directory: `/home/painarise/Documents/Projects/endocare-instagram-posts/`

- `make_posts.py` — full generator (PIL, 1080x1350)
- `post1.png` .. `post4.png` — final renders, quality=95
- `preview.jpg` — 40% 2x2 contact sheet
- `captions.txt` — ready-to-paste caption + hashtags per post

## Campaign arc

1. post1 PROBLEM — "Your patient data is sleeping on someone else's server."
   Pain list: breach & leak risk / downtime & vendor lock-in / surprise fees on
   your own data / compliance burden. Red xmarks; cloud with red X + "YOU DON'T
   OWN IT".
2. post2 SOLUTION — "Hosted on YOUR machine. Not in someone's cloud."
   On-premise server illustration + lock badge; ticks: 100% on-premise, works
   offline, you own the data forever.
3. post3 BENEFITS — "Own your data. Own your clinic." Numbered rows 01-04:
   full data ownership / zero cloud dependency / no per-record fees / patient
   privacy first.
4. post4 CTA — "Ready to bring your EMR home?" Teal "BOOK A FREE DEMO" button
   + contacts: WhatsApp +91 72048 97249 / Call +91 88848 58000 /
   shashiadvancedhealth.com.

## Design system used

- Canvas 1080x1350, margin ML=88; ink gradient INK_TOP (10,29,37) →
  INK_BOT (6,18,24); accent teal (45,212,191); white text (236,246,246);
  muted (146,180,187); amber (245,190,110) for problem-word emphasis.
- Montserrat Black 84-96px headlines, SemiBold 27-33 body, Light 29-33 sub-copy,
  tracked caps (4-5px) for eyebrows.
- Chrome: teal plus-logo + "ENDOCARE EMR" top-left, "01/04" index top-right,
  ghost page number (Black ~330px, alpha 11) upper-right, bottom bar with
  tagline + 4-dot carousel indicator (current = teal).
- Texture: plus signs every 140x150px at alpha 8.

## Bugs hit and fixed (see SKILL.md for the general lesson)

1. ImageDraw alpha gotcha: drawing with alpha directly on an RGBA canvas then
   convert("RGB") renders ghosts opaque. Fixed by drawing on a transparent
   overlay + Image.alpha_composite at save.
2. Verification false positive: the "ghost too bright" sample zone overlapped
   the amber headline (bright by design). Fix: sample provably-empty zones.
3. Oversized patch call timed out mid-stream — broke the fix into 3 small
   replace patches (canvas overlay, save-time composite, contact text size).
4. Post4 contact line ran past the design margin — shrunk REG 29→25 and moved
   the column left (cx0 648→620); final bright bbox x ≤ 960.
