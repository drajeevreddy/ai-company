#!/usr/bin/env python3
"""Pixel-bounds verification for generated poster PNGs (pillow-graphics skill).

Usage:
    python3 verify_pixel_bounds.py post1.png post2.png ...
    python3 verify_pixel_bounds.py --size 1080,1350 'post*.png'

Checks per image:
  1. (optional) exact canvas size
  2. bright-content bbox stays inside the 12px margin band (catches clipped text)
  3. all four corners dark (< 60 max channel) (catches opaque alpha-bleed)

Exits non-zero if any check fails. Sampling stride 2 keeps it fast on 1080x1350.
"""
import glob
import sys

from PIL import Image

BRIGHT = 190      # grayscale threshold for "content"
MARGIN = 12       # px clearance from each edge
CORNER_MAX = 60   # max channel value allowed at corners


def check(path, expected_size=None):
    fails = []
    im = Image.open(path)
    if expected_size and tuple(im.size) != tuple(expected_size):
        fails.append(f"size {im.size} != {expected_size}")

    g = im.convert("L")
    px = g.load()
    W, H = im.size
    bright = [(x, y) for y in range(0, H, 2) for x in range(0, W, 2) if px[x, y] > BRIGHT]
    if bright:
        xs = [p[0] for p in bright]
        ys = [p[1] for p in bright]
        if min(xs) < MARGIN or max(xs) > W - MARGIN or min(ys) < MARGIN or max(ys) > H - MARGIN:
            fails.append(
                f"content bbox ({min(xs)}-{max(xs)}, {min(ys)}-{max(ys)}) "
                f"breaches {MARGIN}px margin on {W}x{H} canvas"
            )

    rgb = im.convert("RGB").load()
    for x, y in [(2, 2), (W - 3, 2), (2, H - 3), (W - 3, H - 3)]:
        if max(rgb[x, y]) > CORNER_MAX:
            fails.append(f"corner ({x},{y}) bright {rgb[x, y]} (alpha-bleed?)")
    return fails


def main(argv):
    expected_size = None
    paths = []
    i = 0
    while i < len(argv):
        if argv[i] == "--size":
            expected_size = tuple(int(v) for v in argv[i + 1].split(","))
            i += 2
        else:
            paths.extend(glob.glob(argv[i]))
            i += 1
    if not paths:
        paths = sorted(glob.glob("post*.png")) + sorted(glob.glob("*.png"))
    if not paths:
        print("no images found")
        return 2

    all_fails = []
    for p in paths:
        try:
            fails = check(p, expected_size)
        except Exception as e:  # noqa: BLE001
            fails = [f"could not open: {e}"]
        if fails:
            print(f"FAIL {p}:")
            for f in fails:
                print(f"  - {f}")
            all_fails.extend(fails)
        else:
            print(f"PASS {p}")
    return 1 if all_fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
