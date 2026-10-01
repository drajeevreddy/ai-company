# Pixel Analysis Techniques for Poster QA

These are the numpy + Pillow techniques used to verify rendered poster batches.

## Blank detection

```python
import numpy as np
from PIL import Image

arr = np.array(Image.open(path).convert('RGB'))
flat = arr.reshape(-1, 3)
sample = flat[np.random.choice(len(flat), min(10000, len(flat)), replace=False)]
unique = len(set(tuple(int(x) for x in p) for p in sample))
# Flag: unique < 50
```

Alternative: check variance of pixel values. Departure from random noise (variance ~3000+) signals blank.

## Margin overflow (light background)

For slides with white/paper background, find non-white content and check bounding box against margins:

```python
diff = np.abs(arr.astype(float) - np.array([255, 255, 255])).max(axis=2)
mask = diff > 30
rows = np.any(mask, axis=1)
cols = np.any(mask, axis=0)
top = np.argmax(rows)
bottom = h - np.argmax(rows[::-1]) - 1
left = np.argmax(cols)
right = w - np.argmax(cols[::-1]) - 1
margin = 72
if left < margin - 12: flag("LEFT_OVERFLOW")
if right > w - 1 - (margin - 12): flag("RIGHT_OVERFLOW")
```

## Footer presence

Bottom 80px region check — footer content should produce dark/varied pixels:

```python
footer = arr[h-80:h-5, :]
footer_diff = np.abs(footer.astype(float) - arr[0,0].astype(float)).max(axis=2)
footer_content = np.sum(footer_diff > 25)
# Flag: footer_content < 100
```

## Dark-background text clipping

On dark slides, check for LIGHT pixels near edges:

```python
light_mask = np.mean(arr, axis=2) > 120
top_light = np.argmax(np.any(light_mask, axis=1))
left_light = np.argmax(np.any(light_mask, axis=0))
# Flag if < 25px from edge
```

## Collision detection (text overlap)

For text-heavy slides (list slides with 4+ items), check row density:

```python
row_dark = np.sum(np.mean(arr, axis=2) < 120, axis=1)
text_rows = np.where(row_dark > 10)[0]
# Group consecutive rows (gap > 5px = new line)
# Check: gap between line groups < 3px = collision risk
```

## Determine background type

```python
corner = arr[0, 0]
is_dark = np.mean(corner) < 60
# Dark: ink #08243C or similar
# Light: paper #FFFFFF or paper2 #F4F8FC
```