#!/usr/bin/env python3
"""Frame-to-frame motion profile for a video file.

Usage
-----
  python3 motion_profile.py MINE.mp4
  python3 motion_profile.py MINE.mp4 --ref REFERENCE.mp4
  python3 motion_profile.py MINE.mp4 --ref REFERENCE.mp4 \
      --sections 0,4,opening 4,9,product 23.5,28,breadth

Reports the mean absolute luma difference between consecutive frames, overall
and per section, plus every stretch where the picture holds still for longer
than --frozen seconds.

This is the numeric answer to "does it move, or is it a slideshow?" — which the
eye cannot settle at 30fps and which the source code cannot answer at all. A
layer can animate by 0.2 px/frame and be perfectly invisible while its comment
claims "continuous motion for the whole beat".

Calibration: below ~1.0 for more than half a second at a time is holding still.
A real continuous camera flight averages around 3.8 overall, with intentional
near-still stretches down at 0.2-0.8.
"""

import argparse
import subprocess
import sys

import numpy as np

# Small enough to be fast, large enough to keep structure worth comparing.
W, H = 192, 108


def probe(path):
    """Return (fps, duration_seconds) for the first video stream."""
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=r_frame_rate",
         "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True, check=True,
    ).stdout.split()
    fps = 30.0
    if out:
        parts = out[0].split("/")
        try:
            num, den = float(parts[0]), float(parts[1]) if len(parts) > 1 else 1.0
            if den:
                fps = num / den
        except ValueError:
            pass
    duration = float(out[1]) if len(out) > 1 else 0.0
    return fps, duration


def frame_deltas(path, w=W, h=H):
    """Mean absolute inter-frame luma delta, one value per frame transition."""
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", path,
         "-vf", f"scale={w}:{h}", "-pix_fmt", "gray", "-f", "rawvideo", "-"],
        capture_output=True, check=True,
    ).stdout
    n = len(raw) // (w * h)
    if n < 2:
        sys.exit(f"{path}: decoded only {n} frame(s) — is this a video?")
    a = np.frombuffer(raw[: n * w * h], dtype=np.uint8).reshape(n, h, w).astype(np.int16)
    return np.abs(np.diff(a, axis=0)).mean(axis=(1, 2))


def frozen_runs(d, fps, thresh=1.0, min_s=0.5):
    """Contiguous stretches where the picture is effectively static."""
    runs, i, n = [], 0, len(d)
    while i < n:
        if d[i] < thresh:
            j = i
            while j < n and d[j] < thresh:
                j += 1
            if (j - i) / fps >= min_s:
                runs.append((i / fps, j / fps, (j - i) / fps, float(d[i:j].mean())))
            i = j
        else:
            i += 1
    return runs


def bars(values, scale=1.0, width=28):
    return "".join("#" * min(width, max(0, int(v * scale))) for v in values)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video")
    ap.add_argument("--ref", help="reference video to compare against")
    ap.add_argument("--sections", nargs="*", default=[],
                    metavar="START,END,LABEL",
                    help="section boundaries in seconds")
    ap.add_argument("--frozen", type=float, default=1.0,
                    help="delta considered static (default 1.0)")
    ap.add_argument("--frozen-min", type=float, default=0.5,
                    help="minimum static stretch to report, seconds (default 0.5)")
    args = ap.parse_args()

    fps, duration = probe(args.video)
    mine = frame_deltas(args.video)
    ref = frame_deltas(args.ref) if args.ref else None

    print(f"{args.video}")
    print(f"  {len(mine) + 1} frames, {fps:g} fps, {duration:.2f}s")
    if ref is not None:
        rfps, rdur = probe(args.ref)
        print(f"  ref frames: {len(ref) + 1}, {rfps:g} fps, {rdur:.2f}s")

    print(f"\n  OVERALL  mine {mine.mean():.2f}"
          + (f"   ref {ref.mean():.2f}   ratio {mine.mean() / ref.mean():.2f}"
             if ref is not None else ""))

    if args.sections:
        print(f"\n  {'section':<14}{'mine':>8}{'ref':>8}{'ratio':>8}")
        for spec in args.sections:
            parts = spec.split(",")
            start, end = float(parts[0]), float(parts[1])
            label = parts[2] if len(parts) > 2 else f"{start}-{end}"
            a, b = int(start * fps), int(end * fps)
            seg_m = mine[a:b].mean() if b <= len(mine) else mine[a:].mean()
            line = f"  {label:<14}{seg_m:>8.2f}"
            if ref is not None:
                seg_r = ref[a:b].mean() if b <= len(ref) else ref[a:].mean()
                line += f"{seg_r:>8.2f}{seg_m / seg_r:>8.2f}"
            print(line)

    print("\n  per-second profile")
    step = int(round(fps))
    for s in range(0, len(mine), step):
        v = mine[s:s + step].mean()
        line = f"    {s / fps:5.1f}s  {v:6.2f}  {bars([v], 1.0, 34)}"
        if ref is not None and s < len(ref):
            rv = ref[s:s + step].mean()
            line += f"   ref {rv:6.2f} {bars([rv], 1.0, 34)}"
        print(line)

    for name, d, f in ([(args.video, mine, fps)]
                       + ([(args.ref, ref, rfps)] if ref is not None else [])):
        runs = frozen_runs(d, f, args.frozen, args.frozen_min)
        print(f"\n  {name}: {len(runs)} static stretch(es) >{args.frozen_min}s")
        for a, b, dur, avg in runs:
            print(f"    {a:.2f}s - {b:.2f}s  ({dur:.2f}s)  avg {avg:.2f}")


if __name__ == "__main__":
    main()
