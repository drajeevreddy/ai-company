#!/usr/bin/env python3
"""Loudness, brightness, stereo width and arrangement shape for a video or audio file.

Usage
-----
  python3 audio_profile.py out/cut.mp4
  python3 audio_profile.py public/music/score.wav

Three numbers decide what is wrong with a score before you write a note:

  integrated LUFS      how loud          ~-14 for streaming/web delivery
  spectral centroid    how bright        ~2000-3500 Hz for an upbeat cut
  per-0.5s RMS bars    arrangement       no unexplained holes

The centroid is the one that catches the two classic failures: a pure-sine
synthesis sits near 800 Hz and sounds muddy, and a broadband reverb impulse
pushes it past 6000 Hz and sounds like hiss.
"""

import argparse
import re
import subprocess
import sys

import numpy as np
from numpy.fft import rfft, rfftfreq

SR = 44100


def ebur128(path):
    """(integrated LUFS, true peak dBFS) via ffmpeg's EBU R128 meter.

    Both values are reported on stderr, and the meter only emits them at
    -v info or above.
    """
    r = subprocess.run(
        ["ffmpeg", "-v", "info", "-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"],
        capture_output=True, text=True,
    )
    lufs = re.findall(r"\bI:\s*(-?\d+(?:\.\d+)?)\s*LUFS", r.stderr)
    peak = re.findall(r"\bPeak:\s*(-?\d+(?:\.\d+)?)\s*dBFS", r.stderr)
    return (float(lufs[-1]) if lufs else float("nan"),
            float(peak[-1]) if peak else float("-inf"))


def decode(path, channels=1, sr=SR):
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", path, "-ac", str(channels),
         "-ar", str(sr), "-f", "s16le", "-"],
        capture_output=True, check=True,
    ).stdout
    if not raw:
        sys.exit(f"{path}: no audio decoded — does this file have an audio stream?")
    x = np.frombuffer(raw, dtype="<i2").astype(np.float64) / 32768.0
    if channels > 1:
        x = x[: (len(x) // channels) * channels].reshape(-1, channels)
    return x


def centroid_profile(mono, sr=SR, win=2048, hop_s=0.25):
    hop = int(hop_s * sr)
    out = []
    for i in range(0, max(1, len(mono) - win), hop):
        seg = mono[i:i + win]
        if len(seg) < win:
            break
        S = np.abs(rfft(seg * np.hanning(win)))
        f = rfftfreq(win, 1 / sr)
        out.append(float((S * f).sum() / (S.sum() + 1e-12)))
    return np.array(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path")
    ap.add_argument("--hop", type=float, default=0.5,
                    help="RMS bar resolution in seconds (default 0.5)")
    args = ap.parse_args()

    mono = decode(args.path, 1)
    dur = len(mono) / SR
    print(f"{args.path}\n  {dur:.2f}s, mono {SR} Hz")

    lufs, peak = ebur128(args.path)
    print(f"\n  integrated loudness  {lufs:8.2f} LUFS    (target ~ -14)")
    print(f"  true peak            {peak:8.2f} dBFS")
    print(f"  sample peak          {np.abs(mono).max():8.4f}")

    cents = centroid_profile(mono)
    if len(cents):
        print(f"  spectral centroid    {cents.mean():8.0f} Hz   "
              f"(muddy <1500, working 2000-3500, hissy >5500)")

    try:
        pair = decode(args.path, 2)
        mid = (pair[:, 0] + pair[:, 1]) / 2
        side = (pair[:, 0] - pair[:, 1]) / 2
        m, s = np.sqrt((mid ** 2).mean()), np.sqrt((side ** 2).mean())
        print(f"  side/mid energy      {s / m if m else 0:8.3f}   (0 = mono, ~0.3 = wide)")
    except (SystemExit, subprocess.CalledProcessError):
        pass

    hop = max(1, int(args.hop * SR))
    rms = np.array([20 * np.log10(np.sqrt(np.mean(mono[i:i + hop] ** 2)) + 1e-12)
                    for i in range(0, max(1, len(mono) - hop), hop)])
    if not len(rms):
        return

    print(f"\n  RMS dB per {args.hop:g}s  (arrangement shape)")
    lo = rms.min()
    for i, v in enumerate(rms):
        fill = int(max(0, (v - lo + 3)) * 1.0)
        print(f"    {i * args.hop:6.1f}s  {v:6.1f}  {'#' * min(fill, 60)}")

    # An unexplained hole is a long stretch far below the median level.
    med = float(np.median(rms))
    quiet = rms < med - 6
    runs, i = [], 0
    while i < len(quiet):
        if quiet[i]:
            j = i
            while j < len(quiet) and quiet[j]:
                j += 1
            if (j - i) * args.hop >= 1.0:
                runs.append((i * args.hop, j * args.hop, (j - i) * args.hop))
            i = j
        else:
            i += 1

    print(f"\n  median RMS {med:.1f} dB")
    if runs:
        print("  stretches >6 dB below median for >=1s (check these are intentional drops):")
        for a, b, d in runs:
            print(f"    {a:.1f}s - {b:.1f}s  ({d:.1f}s)")
    else:
        print("  no unexplained holes >=1s")


if __name__ == "__main__":
    main()
