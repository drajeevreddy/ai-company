---
name: pillow-graphics
description: Poster/social PNGs via Pillow, no headless browser needed.
version: 1.0.0
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [design, pillow, pil, graphics, posters, social-media, instagram, verification]
    related_skills: [claude-design, sketch, ascii-art]
---

# Pillow Graphics — Direct-to-PNG Poster & Social Image Generation

Use when the user wants social media posts (Instagram 4:5, square, stories),
posters, cards, or banner graphics and the environment has NO headless browser (no
chromium/playwright) or no screenshot pipeline. Produces real PNGs with Pillow —
no HTML, no browser needed. claude-design governs HTML artifacts; this skill
governs direct-to-PNG.

Trigger phrases: "make an Instagram post", "create 4 posts", "social media
graphics", "poster/banner images", "4:5 ratio post".

## Environment checks (one terminal call, batched)

- `python3 -c "import PIL; print(PIL.__version__)"` — Pillow present?
- `fc-list | grep -iE "montserrat|inter|poppins|roboto"` — which font families exist
- `which chromium chromium-browser google-chrome` — no browser → PIL route is right

Montserrat is commonly installed on Fedora at
`/usr/share/fonts/julietaula-montserrat-fonts/Montserrat-*.otf` with weights
Thin..Black — ideal for poster hierarchy (Black headlines, SemiBold body,
Light sub-copy, tracked caps for eyebrows).

## Workflow

1. Clarify branding first — one question max (existing brand name vs generic vs new).
2. Canvas sizes: Instagram feed 4:5 = 1080x1350, square = 1080x1080, story 9:16 = 1080x1920.
3. Design system: one dark ink gradient + ONE accent + white/muted text. Ghost page
   numbers (alpha ~11) and a faint texture grid (alpha ~8) add depth cheaply.
4. Use the helper kit in `templates/pil_poster_helpers.py` (copy + adapt).
5. Render PNGs at quality=95; ALSO emit a 40%-scale contact sheet (`preview.jpg`)
   so the user can eyeball the whole set in one file.
6. Verify with `scripts/verify_pixel_bounds.py` (or the inline scan below).
7. Deliver `captions.txt` — ready-to-paste caption + hashtags per post.

## CRITICAL: ImageDraw alpha gotcha (cost real debugging time)

```python
# WRONG — alpha silently dropped on convert("RGB"):
base = vgrad(...).convert("RGBA")
d = ImageDraw.Draw(base, "RGBA")
d.text(..., fill=(236, 246, 246, 8))   # ghost / watermark
base.convert("RGB").save(out)          # ghost renders FULLY OPAQUE
```

Pillow's ImageDraw on an RGBA image stores raw RGBA pixels; `convert("RGB")`
discards alpha instead of compositing. Every semi-transparent element (ghost
numbers, subtle textures, translucent chip fills) comes out opaque.

```python
# RIGHT — draw on a transparent overlay, alpha_composite at save time:
ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(ov, "RGBA")   # draw everything with alpha here
final = Image.alpha_composite(vgrad(W, H, INK_TOP, INK_BOT).convert("RGBA"), ov).convert("RGB")
final.save(out, quality=95)
```

Symptom: bright pixels where ghost/watermark/texture should be faint; background
bleed. Detection: corner darkness check + bright-bbox scan (below).

## Text layout helpers (no text-measuring pain)

- `wrap(draw, text, font, maxw)` — greedy word wrap; `draw.textlength()` for widths
- `wrap_rich(draw, segs, font, maxw)` — word wrap over [(word, color), ...] segments
  for mixed-color headlines (e.g. "Hosted on YOUR machine.")
- `tracked(draw, xy, text, font, fill, tracking)` — letter-spaced caps (tracking 4-12px)
- `chip(draw, ...)` — pill label; height from `font.getmetrics()` asc+desc
- Anchor `"lm"` (left-middle) for vertical centering on a baseline.

## Icons without assets

Draw check/xmark badges as circle (fill = color at alpha 26) + thick lines;
server racks as rounded rects + slots; clouds as overlapping ellipses; lock as
rounded rect + shackle. No emoji, no stock images, no SVG dependencies.

## PITFALL — AI image gen unavailability (cost real debugging time)

User may request "generate images with ChatGPT/DALL-E" or similar. When
Claude/Codex/OpenAI CLI are not authenticated, Ollama times out, and no
OpenAI-compatible server is reachable — do NOT block on it. Pillow is the
correct fallback for social graphics. Generate with PIL directly, then
deliver captions + hashtags separately. Check availability with one call:

```bash
# Quick check — any of these means AI image gen is probably usable:
curl -s http://127.0.0.1:11434/api/tags    # Ollama
curl -s http://127.0.0.1:20128/v1/models  # OpenAI-compatible proxy
which claude codex openai                  # CLI tools
```

If none respond, go straight to Pillow. Do not waste time troubleshooting
unconfigured LLM servers — the user can fix that; you can ship the posts.

## Analyzing existing images

When `vision_analyze` returns a 404 (no endpoints support image input in this environment), use Pillow directly to extract design attributes from existing images:

```python
from PIL import Image
from collections import Counter
img = Image.open(path).resize((50, 50))
pixels = list(img.getdata())
# For RGBA, strip alpha; for RGB, use as-is
if img.mode == 'RGBA':
    pixels = [(r, g, b) for r, g, b, a in pixels]
color_counts = Counter(pixels)
top5 = color_counts.most_common(5)
# Filter out near-white to find accent colors
dark = [(r, g, b) for r, g, b in pixels if not (r > 240 and g > 240 and b > 240)]
avg = (sum(c[0] for c in dark)//len(dark), sum(c[1] for c in dark)//len(dark), sum(c[2] for c in dark)//len(dark))
```

This reveals dominant and accent colors when vision tools are unavailable.

## Verification pattern (run on every render)

Grayscale scan: pixels > 190 = bright. Assert bright-content bbox stays inside
[MARGIN=12, W-12]/[MARGIN, H-12] (catches clipped text), and all four corners are
dark (< 60 max channel) (catches opaque-bleed regressions). Script:
`scripts/verify_pixel_bounds.py`.

PITFALL — false positives: verification sample zones must NOT overlap legitimately
bright content (amber headline, teal button). This session a "ghost too bright"
failure was a false alarm: the sample rectangle covered the amber headline.
Pick provably-empty zones (above the headline, beside a chip) or diff against a
known background pixel.

## Matching an existing brand deck (do this before designing a sibling set)

When the client already has published posts, MEASURE them instead of eyeballing sizes. Guessing
small produced a set that filled only the top third of each 1080x1350 slide, while the client's own
deck ran content to y~1275.

Measure, in one script, on the client's real file:

- **Ink rows per text run.** Scan rows for pixels differing from the sampled background by >40, group
  contiguous rows (gap >6), and print `(top, bottom, height)` per run. A heading line's run height is
  its cap height; font size is roughly `cap_height / 0.70` for most sans families.
- **Line pitch** = distance between consecutive run tops; gives the real line-height multiplier
  (the deck this came from used pitch ≈ 1.0em, much tighter than a default 1.5).
- **Left margin and top rail** = leftmost ink x and the logo/metadata band height.

Then set the generator's constants to those numbers. Two cheap checks after rendering:

- **Rhythm:** first ink row below the header rail should be identical (within ~15px) across every
  slide. If covers and items differ, the type block is jumping as the user swipes.
- **Fill:** scan for the last ink row above the footer rail. If content stops near mid-canvas while
  the client's deck ran to the bottom, the slides read underfilled — raise the type scale.

Low-contrast ghost numerals are a trap: a pale numeral that looks tasteful in a thumbnail can be
invisible on a phone. Either give it enough contrast to read as a deliberate element, or cut it.

## Authoring large generator scripts

- Write the whole generator with ONE write_file, then small targeted patches.
- Keep patch arguments under ~8K tokens: oversized patch calls can time out the
  stream mid-delivery. Break big edits into multiple small replace patches.
- Pyright flags PIL enum attrs (`Image.BILINEAR`, `Image.LANCZOS`) as unknown —
  false positives, runtime is fine.

## Instagram post generation workflow

When the user wants a full social media campaign (7 days of posts,
captions, hashtags, images):

1. **Analyze brand assets first.** Read existing posts via `vision_analyze`,
   extract the palette from reference images with the color extraction
   script below. The palette and design guidelines are the source of truth,
   not vibe-guessing.
2. **Generate images with Pillow.** 1080×1350 for Instagram feed,
   dark ink gradient + ONE accent + white text. See the design system
   in the Workflow section.
3. **Write captions + hashtags.** Bold, concise, brand-voice. One
   per post. Deliver in `captions.txt` or a JSON array with day, type,
   headline, caption, hashtags.
4. **Render a contact sheet** (`preview.jpg` at 40% scale) so the
   user can eyeball the whole set at once.
5. **Verify** with `scripts/verify_pixel_bounds.py` before delivery.

Save the full template to `references/instagram-post-workflow.md`.

## Support files

- `templates/pil_poster_helpers.py` — copy-and-adapt helper kit (gradient,
  overlay compositing, rich wrap, tracked text, chips, icon primitives)
- `scripts/verify_pixel_bounds.py` — re-runnable pixel verification for any PNG set
- `references/endocare-emr-instagram.md` — worked example: EndoCare EMR 4-post
  campaign (layout coords, palette, contacts, output paths)
