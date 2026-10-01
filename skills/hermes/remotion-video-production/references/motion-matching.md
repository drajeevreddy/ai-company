# Matching a cut to a reference video

For requests of the form "make it like this video". The reference is the spec — extract
numbers from it before deciding anything.

## The method

1. **Probe the reference and your cut for the same facts.**

   ```bash
   ffprobe -v error -show_streams -show_format REFERENCE.mp4
   ```

   Record duration, frame rate, resolution, and **whether the reference even has an audio
   track**. A video-only download has no music to extract; if the request says "use the
   reference's song", that is impossible and needs saying up front rather than discovering
   after an hour of work.

2. **Build a contact sheet and look at it.** One frame per second, tiled, is enough to read
   the visual language and the sequence of ideas.

   ```bash
   ffmpeg -v error -i REFERENCE.mp4 -vf "fps=1,scale=480:-1,tile=6x6" \
       -frames:v 1 sheet.png -y
   ```

   Then a finer pass (3 fps, 12s at a time) when you need to read the *motion* rather than
   the composition. Read the images with vision — do not infer motion from a description.

3. **Measure inter-frame motion on both, then compare per section.** This is the step that
   turns "it feels static" into a number and a location.

   ```bash
   python3 scripts/motion_profile.py MINE.mp4 --ref REFERENCE.mp4 \
       --sections 0,4,open 4,9,a 9,14,b 14,19,c 19,23.5,d 23.5,28,e 28,33,close
   ```

4. **Read the profile shape, not just the overall mean.** A mean that matches while the
   per-section shape does not is still a mismatch. A real reference typically opens close to
   still, peaks hard through its busiest sections, and resolves to near-stillness on the
   closing lockup. Constant motion at the right average is wrong and also tiring to watch.

5. **Fix the structural cause, then re-measure.** Never report a fix you have not measured.

## What actually produces visible motion

Two independent conditions, and both must hold. Getting one right and not the other is the
usual reason an added layer changes nothing.

**Amplitude.** Something must traverse whole pixels per frame. Convert the code into
px/frame before believing it:

```
Math.cos(frame / 110) * 26       ->  26 * (1/110)        =  0.24 px/frame   invisible
push 34 -> -46 over 150 frames   ->  80 / 150            =  0.53 px/frame   invisible
speed={11}                       ->  11 px/frame         =  visible
```

A term of the form `Math.sin(frame / N) * A` has a maximum slope of `A / N` px per frame.
That single division tells you whether the layer is doing anything.

**Spatial detail.** A smooth panel sliding five pixels barely changes any sample. A panel
carrying real UI — text lines, chips, a screenshot — has high spatial frequency, so even a
two-pixel step moves a lot of samples. This is why "add a moving gradient" never registers
in the measurement but "slide the product screenshots across" does immediately.

Combined rule: **the highest-value depth layer is a conveyor of real product imagery
traversing the frame**, because it has both amplitude and detail. A blank glass panel is
worth approximately nothing regardless of how far it travels.

## Root-cause checklist when a layer has no measurable effect

Work these in order — the first one is the most common and the least obvious.

1. **Is an opaque background painted above it?** If each scene renders its own full-bleed
   canvas, everything the composition mounts beneath those scenes is covered. The symptom is
   precisely "I added a layer and the metric did not move". Confirm it: render a still at a
   frame where the layer should be prominent and *read the image*. Then remove the per-scene
   repaint and re-measure a segment.
2. **Is the container flattening 3D?** A `perspective` on a child inside a `preserve-3d`
   ancestor collapses that ancestor's rotation and translation into a flat plane. Depth
   elements need a flag for whether to supply their own perspective, depending on which side
   of the camera rig they are mounted.
3. **Is alpha alone carrying it?** At low alpha on a near-white page it is invisible to both
   the eye and the metric. Raise alpha *and* add detail; raising only alpha on a flat panel
   still measures nothing.
4. **Is the amplitude sub-pixel?** Do the `A / N` division above.
5. **Is the measurement window hiding it?** A layer that only moves during a reveal can be
   genuine and still invisible in a section average. Check the per-second profile, not just
   the section mean.

## The motion envelope

Once several layers carry movement, drive them all from one scalar so the piece has an arc
and a single tuning point. Keep the table in the grid/timing module next to the section
boundaries and interpolate it with a smoothstep so there are no corners the eye can catch:

```ts
export const MOTION_ARC = [
  { bar: 0.0, gain: 0.05 },   // opening — reference sits near still here
  { bar: 3.0, gain: 1.00 },   // the field comes up
  { bar: 7.0, gain: 1.50 },   // busiest section
  { bar: 14.0, gain: 0.20 },
  { bar: 15.0, gain: 0.06 },  // resolves to held
];
```

Then multiply every layer's strength by `motionAt(frame)`. Tuning becomes one edit.

## Fades are not neutral

A fade from the background colour changes every pixel in the frame at once. Measured, a
four-frame fade scored **8.6** on the opening second and **8.9** on the closing second where
the reference read **0.34** and **0.03**. It is the single largest frame-delta event in most
compositions, it swamps whatever is actually happening at the ends, and a reference cut that
cold-opens on a live frame does not have one. Delete it and re-measure.

## What cannot be matched

A reference's sharpest peaks often come from **hard discrete events** — windows slamming in,
full-frame wipes, hard cuts. A single-take composition on a continuous camera flight
structurally cannot produce them: its motion is smooth and its peaks are lower.

Do not close that gap by adding cuts, which breaks the grammar the composition was built on.
Report it: overall density and the shape of the arc match, the discrete-event peaks do not,
and here is why. Quantify it — "reference peaks at 11–13, this tops out around 6" — so the
user can decide whether the trade is worth it.
