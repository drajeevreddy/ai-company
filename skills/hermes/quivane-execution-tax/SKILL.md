---
name: quivane-execution-tax
description: "Use when building a Quivane Execution Tax episode."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [remotion, quivane, motion-graphics, video, education, sound-design]
    requires_tools: [terminal, read_file, patch, write_file]
    requires_toolsets: [hermes-cli]
---

# The Execution Tax — Quivane educational series

A six-episode educational motion-graphics series aimed at business owners. Each
episode takes one decision they make constantly, plays it out, and runs a cost
counter in the corner that climbs as the mistake unfolds.

Deliberately NOT the `QuivaneSizzle` look. That cut is gloss, product screenshots
and camera flight. This series is typography, rules and diagrams on paper — no
cards, no shadows, nothing rendered. The restraint is the point: it is the
opposite of what gets read as AI-generated content, which is a live problem for
this account.

## Layout

```
~/quivane-launch/
  src/edu/script.ts        episode content + beat map — EDIT THIS PER EPISODE
  src/edu/chrome.tsx       Paper, Chrome, CostCounter, SectionTag, TimeBar, BeatDots
  src/edu/Rail.tsx         Rail (stage timeline) and Fan (divergence diagram)
  src/edu/sections.tsx     the seven sections + SECTIONS assembly array
  src/EducationalComposition.tsx
  generate-edu-music.py    the score, mastered to -14 LUFS
```

Registered in `src/Root.tsx` as `QuivaneEducation01`.

```bash
npx remotion still QuivaneEducation01 /tmp/x.png --frame=480   # verify
npx remotion render QuivaneEducation01 out/ep.mp4 --concurrency=6
python3 generate-edu-music.py                                  # after beat-map edits
```

## Adding an episode

1. Edit `src/edu/script.ts`: `EPISODE`, the copy arrays, `SECT`, the `*_AT` reveal
   frames, `COUNTER_STEPS`.
2. Edit `src/edu/sections.tsx` if the episode needs a different diagram shape.
3. Mirror the timing changes in `generate-edu-music.py` (`COUNTER_STEPS`,
   `SECTION_FRAMES`). **The Python file duplicates the beat map by necessity** —
   it has no way to import TypeScript. Both files print their event lists so a
   mismatch is visible rather than silent. Check them against each other after
   every timing change.
4. `npx tsc --noEmit`, render stills, then render.

## The beat map convention

Every timing constant in `script.ts` is an **absolute frame**, and each section
rebases through a local `rel()` helper because Remotion `<Sequence>` children see
a local `useCurrentFrame()`:

```ts
const abs = (sectionFrom: number) => (absolute: number) => Math.max(0, absolute - sectionFrom);
const rel = abs(SECT.chain.from);   // inside the section component
const lands = CHAIN_AT.map(rel);    // absolute -> local
```

Getting this wrong is silent — reveals land in the wrong place and nothing
errors. If a reveal is early or late, check `rel()` first.

## Colour discipline

**Red means cost.** Paper and type are neutral; the only red in the frame is the
cost counter, the red rail, the comparison panel, and small structural accent
marks. Do not spend red on anything else — the whole rhetorical effect is that by
the third episode the viewer reads red as money leaking before they read a number.

This forces one repeated chore: anything that sits over the red comparison panel
must invert or it disappears. Four elements need this and all four are handled in
`EducationalComposition.tsx`: `Chrome`, `SectionTag`, `TimeBar` (splits at the
panel edge), `BeatDots`.

## The score

`generate-edu-music.py` builds a full bed from numpy: a ticking clock on eighths
that doubles to sixteenths as the cost accelerates, kick/clap/hat, a sixteenth FM
arpeggio, detuned pads, risers into each section turn, and impacts on the
comparison and the brand resolve. `Am–F–Dm–E` — the major V in a minor key is
what makes it sound unresolved, which is the point.

Counter thumps and the demo thud are mixed **into the same file** with the bed
ducked under each one, so the composition only loads one audio source.

```
python3 generate-edu-music.py
# prints: final LUFS, true peak, and the per-section layer levels
```

Targets −14 LUFS integrated, −1 dBTP ceiling, verified after MP3 encode because
LAME overshoots.

**A sparse score was tried first and was wrong.** Seven sounds, no bed, on a
42-second feed video is 42 seconds of dead air. Do not reduce the score to sound
design.

## Continuous motion is mandatory

`TimeBar` (fills 0→42s continuously) and `BeatDots` (four squares lighting on the
120 BPM beat) exist because a measurement of the first cut found stretches of
**up to nine seconds where not one pixel changed**. The diagrams are static by
design, but a frozen frame for nine seconds reads as a broken video, not a calm
one.

Keep both. They are the cheapest continuous motion available and they also lock
the picture to the music without a single cut.

## Verification traps

These all cost real time. Check them rather than trusting the code.

**Rail/Fan `lands` array length must equal the `stages` array length.** A rail
passed 4 stage nodes with a 2-entry `lands` array read past the end, produced
`undefined` in an `interpolate` input range, and threw
`inputRange must contain only numbers` — killing six frames of the episode. The
error names neither the component nor the array.

**`interpolate` requires an ASCENDING input range.** `interpolate(z, [3000, 2160], ...)`
throws. Feed it ascending and swap the output pair.

**Area-diff motion metrics are blind to thin-line animation.** Measuring a
42-second piece of hairlines, small type and rules gave "1225 of 1259 frames
static" — a false reading, because the metric measures changed pixel *area* and a
1px line drawing itself registers as nothing. Verify rail and fan build-ups
**perceptually** with a frame strip (`select=eq(n\,A)+eq(n\,B)...,tile=2x2`), not
with a delta score.

**Never put `rgba()` alpha AND a CSS `opacity` on the same element.** The
metronome dots had `rgba(255,255,255,0.42)` with `opacity: 0.42`, multiplying to
0.18 effective — invisible. Put the alpha in the colour and set opacity to 1.

**Sections must not open on dead frames.** A section whose first reveal lands at
local frame 40 cuts to 1.3 seconds of near-empty page. Keep first reveals inside
~16 frames of a section start. The worst case measured a single-frame delta of
95.5 cutting from the red panel to a near-blank frame — a visible flash.

**Long holds need staggered reveals.** Spread reveals across the section rather
than front-loading them. The comparison episode staggers its eight list items
14 frames apart so the longest section keeps producing new information.

**A full-bleed coloured panel breaks every fixed-colour chrome element at once.**
Render a still at the panel's midpoint and read it before rendering the episode.

## Writing rules for the copy

This series only works if it does not read as generic. Hold the copy to:

- Name the specific thing. "make it modern" beats "unclear requirements".
- No slogans. If a line would work on a poster it is doing no work.
- Vary sentence shape. Four sentences of the same length is a tell.
- No "it's not just X, it's Y". No "X is the language of Y".
- Run the `avoid-ai-writing` skill on the script before rendering.

**Never invent business numbers.** A made-up cost counter reads exactly like AI
content, which is the trap this series exists inside. The week figures in `STAGES`
and `REBUILD` are placeholders — they must be replaced from real projects before
an episode ships. This applies with extra force here because the account has
already been hurt once by content that read as generated.
