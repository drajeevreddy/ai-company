# Instagram Post Generation Workflow

End-to-end recipe for generating a multi-day Instagram campaign:
brand analysis, image generation, captions, and delivery.

## Step 1: Analyze brand assets

Extract the color palette from existing brand materials before
designing anything. Use Pillow when `vision_analyze` is unavailable:

```python
from PIL import Image
from collections import Counter

def extract_palette(path, n=8):
    img = Image.open(path).resize((50, 50))
    pixels = list(img.getdata())
    if img.mode == 'RGBA':
        pixels = [(r, g, b) for r, g, b, a in pixels]
    return Counter(pixels).most_common(n)

# From a post image: extract dominant + accent colors
palette = extract_palette('brand_post.png', n=8)
```

Filter out near-white to find accent colors:

```python
dark = [(r, g, b) for r, g, b in pixels if not (r > 240 and g > 240 and b > 240)]
avg = (sum(c[0] for c in dark)//len(dark),
       sum(c[1] for c in dark)//len(dark),
       sum(c[2] for c in dark)//len(dark))
```

## Step 2: Generate post images

Use 1080×1350 for Instagram feed, 1080×1080 for square, 1080×1920 for stories.
Design system: one dark ink gradient + ONE accent + white/muted text.

Key rules:
- Ghost page numbers at alpha ~11, texture grid at alpha ~8
- Draw on RGBA overlay, alpha_composite at save time (NOT convert("RGB") first)
- Render at quality=95
- Emit a 40%-scale contact sheet (preview.jpg) for quick review

## Step 3: Write captions + hashtags

Format per post:
- **Type**: Static / Carousel / Reel / Story
- **Headline**: Bold, short (3-6 words)
- **Caption**: 2-5 sentences, brand voice (direct, opinionated, no AI-slop)
- **Hashtags**: 10-15 relevant tags, mix broad + niche
- **Tag**: @mentions if applicable

Deliver as JSON or a `captions.txt` file.

## Step 4: Verify

Run `scripts/verify_pixel_bounds.py` on every rendered PNG before delivery.
Check: bright-content bbox stays within margins, corners are dark (no opaque-bleed).

## Step 5: Deliver

Package: post images + captions file + contact sheet (preview.jpg).
User can then upload directly to Instagram or schedule via their tool.
