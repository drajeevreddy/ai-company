---
name: poster-qa
description: QA batches of rendered poster PNGs against a spec.
---

## Always-on rules

1. **Report PASS/FAIL + exact filenames.** No prose. Lead with the verdict. List defect filenames exactly.
2. **SPEC.md is ground truth.** Margins (usually 72px), dimensions, required elements, and brand tokens come from the project SPEC. Check SPEC first; do not assume.
3. **Content JSON is the copy source of truth.** Verify poster copy against the JSON (carousels.json, posts.json, captions.json, or equivalent), not from memory.
4. **Touch only the deliverable.** Write only the POSTING-PLAN.md (or whatever the work order specifies). Read-only elsewhere.

## Procedure

### Step 1 — Inventory check

List all expected files. Confirm count and naming pattern match the spec.

```python
import os
base = "path/to/out"
files = sorted(os.listdir(base))
print("Files: %d" % len(files))
```

Expected count = carousels × slides (e.g., 10 carousels × 6 slides = 60 files).

### Step 2 — Dimensions and format

Check every file is the correct dimensions and format. Use PIL.

```python
from PIL import Image
img = Image.open(path)
assert img.size == (1080, 1350), "%s wrong size: %s" % (path, img.size)
assert img.format == 'PNG', "%s not PNG: %s" % (path, img.format)
```

### Step 3 — Blank/empty detection

Check pixel variance. A slide with very few unique colors or near-zero variance is blank.

```python
import numpy as np
arr = np.array(img)
flat = arr.reshape(-1, 3)
unique = len(set(tuple(int(x) for x in p) for p in flat[::max(1, len(flat)//10000)]))
# Flag if unique_colors < 50
```

### Step 4 — Background-aware margin check

**Pitfall: Dark-background slides have full-bleed backgrounds by design.** Checking content near ALL edges flags every dark slide as overflowing. Differentiate by background type first:

```python
corner = arr[0, 0]
is_dark_bg = np.mean(corner) < 60
```

- **Dark background** → check for LIGHT text/graphics near edges (actual clipping risk).
- **Light background** → check for DARK content exceeding margins (e.g., 72px).

```python
bg_color = arr[0, 0]
diff = np.abs(arr.astype(float) - bg_color.astype(float)).max(axis=2)
mask = diff > 30
# Then check bounding box of mask vs margins
```

**Pitfall: Full-bleed backgrounds on covers/CTAs are normal.** Only light-content pixels on dark slides (or dark-content pixels on light slides) near edges are real defects.

### Step 5 — Footer and disclaimer verification

**Pitfall: Footer can be missing even when body content looks fine.** Check the user-specified or SPEC-confirmed y-band — NOT the bottom N pixels by default. The footer band varies by project (e.g., y~1196-1266); the bottom ~80px may be intentionally blank. Confirm the band BEFORE flagging missing footers.

```python
# Get footer band from user or SPEC — do NOT default to bottom 80px
footer_y_start = 1196  # user/spec confirmed
footer_y_end = 1266
footer = arr[footer_y_start:footer_y_end, :]
footer_diff = np.abs(footer.astype(float) - arr[0,0].astype(float)).max(axis=2)
footer_content = np.sum(footer_diff > 25)
# Flag: footer_content < 100
```

If the SPEC requires contact info or a disclaimer, verify those strings appear as rendered text (OCR or visual check). Pixel density alone confirms presence but not accuracy.

### Step 6 — Headline presence

Check top 180px has content. Compare against expected headline from content JSON.

```python
top = arr[0:180, :]
top_dark = np.sum(np.mean(top, axis=2) < 120)
# Flag if top_dark < 200 (suspiciously empty for a headline slide)
```

### Step 7 — Content accuracy

Cross-reference poster text with content JSON. If a `posts.json` (consolidated) does not exist, check split files (e.g., `posts-1-5.json`, `posts-6-10.json`). Use whichever contains the data.

### Step 8 — Report

Format: **Verdict: PASS** or **Verdict: FAIL**.

List each defect with the exact filename. No prose beyond the verdict and defect list.

## Common patterns

### Checking for clipped text on dark slides

On dark-background slides, text is typically light/coral colored. Check if light pixels appear within 25px of any edge:

```python
light_mask = np.mean(arr, axis=2) > 120
# Check bounding box of light_mask near edges
```

### Content filename convention

Posters may be named by slug (`hba1c-explained.png`) or by slide number (`01-cover.png`). Check the SPEC or existing files for the convention. Do not assume.

### Split content JSON files

When `content/posts.json` doesn't exist, content is often split across numbered files like `posts-1-5.json` and `posts-6-10.json`. Merge them before processing:

```python
import json, subprocess
r1 = subprocess.run(['cat', 'content/posts-1-5.json'], capture_output=True, text=True)
r2 = subprocess.run(['cat', 'content/posts-6-10.json'], capture_output=True, text=True)
all_posts = json.loads(r1.stdout)['posts'] + json.loads(r2.stdout)['posts']
```

## References

- `references/pixel-analysis.md` — Detailed PIL/numpy techniques for poster QA