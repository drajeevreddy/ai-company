---
name: remotion-video-production
description: "Use when building or revising a Remotion composition."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [remotion, video, react, motion-graphics, soundtrack, mastering]
    editorial_name: Remotion Video Production
    editorial_description: "Author and revise Remotion compositions: deterministic frame-driven code, motion measured against a reference, and a soundtrack that is mastered rather than guessed at."
    requires_tools: [terminal, read_file, write_file, patch]
    requires_toolsets: []
    requires_plugins: []
---

# Remotion Video Production

Remotion renders React to video one frame at a time. This skill covers authoring and
revising a composition, and the measurement discipline that separates a real revision
from a guess.

## Rule one: measure before and after

A request to "make it move more", "the song is bad, fix it", or "make it like this
reference" cannot be verified by eye at 30fps. Source code cannot answer it either — a
layer can animate by 0.2 px/frame and be perfectly invisible, while claiming in a comment
that it has "continuous motion for the whole beat".

Measure both artifacts, compare their profiles, fix the structural cause, re-measure.
Two probes ship with this skill and are the whole basis for every claim you make:

```bash
python3 scripts/motion_profile.py MINE.mp4 --ref REFERENCE.mp4 \
    --sections 0,4,opening 4,9,product 9,14,product2 23.5,28,breadth
python3 scripts/audio_profile.py out/cut.mp4
```

- `motion_profile.py` reports the mean absolute inter-frame luma delta, overall and per
  section, plus every stretch where the picture holds still for over half a second.
- `audio_profile.py` reports integrated LUFS, true peak, spectral centroid, stereo width,
  and a per-0.5s RMS bar profile that reveals arrangement holes.

Read `references/motion-matching.md` before matching a cut to a reference, and
`references/soundtrack-mastering.md` before writing or repairing a score.

### Calibration anchors

Useful scale for reading the motion profile, from a real 33s reference cut and a revision
of it:

| Signal | Reads as |
|---|---|
| mean delta ~1.2 | slideshow — the "continuous motion" in the code is sub-pixel |
| mean delta ~3.8 | an actual continuous camera flight |
| a stretch of ~0.2–0.8 for >0.5s | an intentional near-still beat; fine in the opening and close |
| a single second spiking to 8+ | a fade, a hard cut, or a full-frame wipe |
| spectral centroid ~790 Hz | a muddy, low-mid score |
| spectral centroid ~3000 Hz | bright but not hissy — the working range for an upbeat cut |
| spectral centroid ~6400 Hz | overcorrected; broadband hiss over the whole mix |

## Non-negotiables when authoring

1. **No `Math.random()`** — use `random("seed")` from remotion. Renders are sharded across
   worker processes; unseeded randomness gives each shard different frames and a render
   that never reproduces.
2. **No CSS `animation` or `transition`.** Remotion may render frames out of order and in
   parallel. Every value must be a pure function of `useCurrentFrame()`.
3. **`interpolate()` input ranges must be strictly monotonically increasing.**
   `interpolate(z, [3000, 2160], ...)` throws `inputRange must be strictly monotonically
   increasing`. Feed the range ascending and reverse the output values instead.

   ```ts
   // wrong — descending input range
   const fade = interpolate(z, [DEPTH, DEPTH * 0.7], [0, 1]);
   // right — ascending input, reversed output
   const fade = interpolate(z, [DEPTH * 0.7, DEPTH], [1, 0]);
   ```

4. **One background per composition, owned at the top.** A scene that paints its own
   full-bleed canvas covers everything mounted beneath it, so composition-level layers
   appear to do nothing at all. Removing the per-scene repaint is often the entire fix for
   "the layer I added isn't visible".
5. **A CSS `perspective` container nested inside a `preserve-3d` ancestor flattens that
   ancestor's camera travel.** Give a depth element a flag so its own `perspective` is off
   when mounted inside the camera rig and on when mounted outside it.
6. **Do not fade in from background colour unless the reference does.** A fade changes every
   pixel at once, so over even four frames it measures a larger frame delta than any real
   content motion — it dominates the opening and closing readings and hides what is actually
   happening there. Cut it, then re-measure the ends.
7. **Alpha alone is not visibility.** On a near-white page, a moved layer at low alpha is
   both invisible to the eye and immovable in the metric. Spatial detail — text, screenshot,
   hairline rules — is what moves samples. A flat panel of the same alpha barely registers.
8. **Honest data only.** Never invent a business figure. If the composition has a figures
   table, that table is the complete list of permitted numbers.

## Iterating

- **Stills, not renders.** `npx remotion still <Comp> out/x.png --frame=N` returns in
  seconds. A 33s 1080p30 render takes about 5 minutes. Place stills on the section
  boundaries from the spec and then actually read the images — a frame that "should" show a
  layer is not evidence that it does. This is the only reliable way to catch a layer being
  covered.
- **Full renders go to the background.** `background=true` with `notify=true`;
  `--concurrency=6` on a normal desktop. A bounded segment
  (`npx remotion render <Comp> out/seg.mp4 --frames=135-410`) takes ~2 min and is enough to
  measure one section — use it while iterating.
- **Typecheck is the gate, not lint:** `npx tsc --noEmit` must be clean. These projects
  often run with `noUnusedLocals` on, so deleting a component means deleting its import in
  the same edit or the typecheck fails.
- **Wire the dial before you tune.** When several layers share one strength, expose a single
  scalar (a motion envelope table, a `strength` prop) and multiply them by it. Tuning then
  becomes one number instead of an edit in six files.

## Reporting

Lead with the measured numbers, not the process: before/after for each metric, and the
ratio against the reference per section. State plainly which sections you could not bring
into line and why — a structural mismatch (a reference that gets its peaks from hard cuts,
which a single-take composition cannot produce) must be reported as a limit, not smoothed
over. Give the absolute path of the rendered artifact.

## Pitfalls

- **A successful render is not a verified result.** Measure it. Gains arrive one layer at a
  time, and an attempt that changes nothing measurable looks exactly like one that worked
  until the numbers say otherwise.
- **Tune brightness with the spectral centroid, not by assumption.** An overcorrection
  toward "brighter" lands around 6400 Hz and sounds like hiss. Fixing it means darkening the
  reverb impulse and deleting 16th-note percussion, not lowering a master gain.
- **Do not restate the project's own spec back to the user as findings.** These projects
  carry their own SPEC files with hard rules (grid, palette, component inventory). Read them,
  obey them, and spend the report on measurements and limits instead.
- **Read a beat's local clock carefully.** Beats mounted inside a `<Sequence>` see
  `useCurrentFrame()` as LOCAL (0 → beat duration), not the global timeline. Rebasing
  constants through a `rel()` helper is the established pattern; using a global frame
  directly puts every reveal in the wrong place.

## Reference

- `references/motion-matching.md` — the full method for matching a cut to a reference, the
  amplitude-versus-detail insight, and what cannot be matched without breaking the grammar.
- `references/soundtrack-mastering.md` — synthesising and mastering a score in numpy/scipy,
  voice designs, the mastering chain, and the measured failure modes.
- `scripts/motion_profile.py` — inter-frame motion profile and still-stretch detector.
- `scripts/audio_profile.py` — LUFS / true peak / spectral centroid / arrangement shape.
