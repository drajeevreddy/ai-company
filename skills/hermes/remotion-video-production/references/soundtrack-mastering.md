# Synthesising and mastering a video score

For "the music is bad, fix it" and for scoring a cut from scratch. Applies to any video
soundtrack, not only Remotion projects.

## Measure first

```bash
python3 scripts/audio_profile.py out/cut.mp4
```

Three numbers decide what is wrong before you write a note:

| Metric | Meaning | Working range |
|---|---|---|
| integrated LUFS | how loud | ~-14 for streaming/web delivery |
| spectral centroid | how bright | ~2000–3500 Hz for an upbeat cut |
| per-0.5s RMS bars | arrangement shape | should have no unexplained holes |

Use ffmpeg's EBU R128 meter as the authority rather than estimating from peaks:

```bash
ffmpeg -v info -i score.wav -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I|Peak):"
```

`I:` is integrated LUFS, `Peak:` is dBFS. Both appear on stderr, so parse stderr — and pull
`-v info` up, since the default log level may not emit them.

## The failure mode to avoid

A hand-rolled score built from stacked sine partials with no reverb, no bus processing and no
loudness target measures like this: **centroid ~790 Hz, integrated ~-19 dB, sample peak
0.65**. That is a dark, muddy, quiet track with a fifth of its headroom thrown away. It does
not sound like music; it sounds like a test tone with a beat.

Three things were missing, and they are the three things to add:

1. **High-frequency content.** FM bells, metallic hats, shakers, shimmer. Nothing in a
   pure-sine synthesis reaches the top octave, so the centroid sits low and the mix is dull.
2. **Space.** A reverb send and a delay on the lead. Dry sums sound like a MIDI file.
3. **Mastering.** EQ, glue compression, limiting, and a measured loudness target.

## Voice designs that work

Quick recipes; each is a handful of lines of numpy.

- **Kick** — three layers, then soft-clip: a sub sine sweeping 160 → 46 Hz with
  `exp(-t/0.028)` on the sweep and `exp(-t/0.185)` on the body; a body tone at ~168 Hz plus
  its second harmonic decaying in 55 ms (this is what survives a phone speaker); and a click
  of high-passed noise plus a 2.1 kHz sine decaying in 3–5 ms. `tanh` clip the sum.
- **Clap** — band-passed 900–4200 Hz noise, with an envelope made of four offset bursts
  (0, 9, 19, 30 ms) each decaying in ~11 ms, plus one long 155 ms tail. Bursts alone read as
  a snare; bursts plus tail read as a clap.
- **Hats** — metallic character comes from summing inharmonic ratios (2.00, 3.01, 4.17,
  5.43, 6.79, 8.21 × a ~620 Hz base), high-passed around 4.6 kHz, **then** low-passed around
  8 kHz. That low-pass is not optional; without it the hats add hiss across the whole mix.
  Decay 15–20 ms closed, 75 ms open.
- **Lead / arp** — two-operator FM, `sin(2πft + β·sin(2πf·2.01t)·exp(-t/0.09))` with
  β ≈ 3.4. The fast-decaying modulation index is the strike; a ratio slightly off 2.0 keeps
  it from sounding like a square wave.
- **Pad** — a detuned saw stack (4–5 voices, ±16 cents, random phase) with a slow filter
  opening: crossfade a low-pass at 700 Hz into one at 2.6 kHz over ~1.6 s. Render L and R
  with different seeds so the pad fills the field.
- **Bass** — saw stack through a filter envelope: crossfade an open low-pass (3 kHz) into a
  closed one (260 Hz) with the open one decaying over ~110 ms. Then drive it.
- **Riser** — noise high-passed at a frequency sweeping up with progress, multiplied by
  `progress ** 1.6`, plus a rising tone and a rising sub.
- **Impact** — a downward sub sweep on `exp(-t/0.55)`, low-passed noise, and a short reversed
  swell before the transient so the hit has a run-up.

## Space

A synthetic impulse response beats no reverb. Generate exponentially decaying noise, and
**darken it as it decays** — process it in chunks with the low-pass cutoff falling from
~6 kHz to ~700 Hz. Also decorrelate the channels (mix a delayed copy of one into the other) so
the tail fills the stereo field.

> **The pitfall that costs the most time:** a broadband IR makes the whole mix hiss. The
> reverb convolves over everything and adds high-frequency noise everywhere, so the centroid
> jumps by thousands of Hz and the track sounds like static instead of like a room. If the
> score measures far too bright, darken the IR *before* touching percussion levels.

Convolve the send bus with `scipy.signal.fftconvolve`, give the process extra buffer length
for the tail, then fold the tail back into the final window with a decaying envelope so the
duration stays exact.

A ping-pong delay on the lead — alternating L/R taps at `feedback ** i`, band-limited to
260–7200 Hz — keeps repeats from turning to mud.

## Arrangement

- **Punctuate the picture.** Take the composition's section boundaries (bars, frame numbers —
  whatever the grid module defines) and land an accent on every one: a cymbal, a riser into
  it, a chord change. Picture and score should articulate the same joints.
- **Drop before the biggest hit.** A half-bar of near-silence before the brand impact makes
  the impact land. Also duck the reverb send there so the hit reads dry and close.
- **Move on the weak beats too.** Side-chain a short duck on every kick so the mix breathes.
- **Four to six notes is enough for a hook.** A short melodic figure stated quietly, then
  restated an octave up with the drums, then climbed at the lift, reads as a composed score.
- **Do not hold a long note in a sparse intro.** A two-beat note in a four-bar intro leaves a
  hole — verify with the RMS profile. One note per beat keeps the opening supported.

## Mastering chain

Order matters; this is the sequence that produced a usable master.

1. High-pass ~30 Hz to remove rumble.
2. Narrow notch at ~330 Hz, −3 dB — this is where stacked low-mid content piles up and makes
   everything sound muddy.
3. Presence peak at ~2.6 kHz, +1.5 dB.
4. Air shelf at ~8.5 kHz, +1.5 dB. Keep this modest; the reverb and percussion already
   supply top end.
5. Bus glue compression — stereo-linked, threshold ≈ −13 dB, ratio ≈ 2.4, attack 12 ms,
   release 200 ms, 6 dB soft knee.
6. Soft clip, then a look-ahead limiter with a true-peak ceiling.
7. **Measure the integrated loudness on a real written file, compute the correction, apply
   it, then measure again.** Do not normalise to a target peak and hope.

Watch for lossy-encoding overshoot: MP3 can decode above the file's sample peak. Measure the
**decoded** true peak and apply a corrective trim if it crossed the ceiling.

## Sequencing the implementation

Iterate in this order; each step is measurable before the next:

1. Build the voices and write the WAV.
2. Listen to the *profile*, not the file: centroid and per-0.5s RMS bars. Fix holes and
   brightness imbalance here.
3. Add space, re-measure the centroid.
4. Master, measure LUFS, apply the correction, re-measure.
5. Encode, then verify the decoded true peak.

Expect at least one round of brightness correction. The first pass typically overshoots.
