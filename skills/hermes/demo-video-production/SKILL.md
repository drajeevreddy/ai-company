---
name: demo-video-production
description: Use when a project demo video is needed.
---

# Demo Video Production (screen recording + AI voice)

Produce polished project demo videos WITHOUT a desktop GUI: narration drives the timeline,
an automated recorder captures the app, ffmpeg muxes them. Proven end-to-end on a hackathon
submission (2-min narrated walkthrough rendered fully headless).

## Workflow (order matters)

1. **Write the narration script FIRST — the voice is the clock.**
   - Conversational, human phrasing. Short sentences. Explain what the viewer sees while they see it.
   - NO self-introduction with the user's name unless explicitly requested (user corrected this).
   - No marketing slop ("revolutionary", "seamlessly") — describe behavior plainly.
2. **Generate TTS** with the `text_to_speech` tool. For THIS user: **male voice,
   mid-30s engineer tone, relaxed and understated — they reject announcer-y/AI-sounding delivery**.
   Forward style guidance via `instructions`; save to `<project>/demo-video/narration.mp3`.
3. **Measure real duration**: `ffmpeg -i narration.mp3 -f null - 2>&1 | grep Duration`.
4. **Plan recording beats** mapped to narration timestamps (e.g. fire mission A when the voice
   introduces it). Trigger app actions over HTTP during recording; never hand-drive.
5. **Record the screen** — see `references/webcmd-headless-recording.md` for the full
   headless-safe capture recipe (works even when cua-driver/browser tools are unusable).
6. **Mux**: `ffmpeg -y -i screen.webm -i narration.mp3 -c:v libx264 -preset veryfast -crf 26
   -pix_fmt yuv420p -c:a aac -b:a 128k -shortest -movflags +faststart final.mp4`.
7. **QC GATE — mandatory.** Extract frames at key beats
   (`ffmpeg -ss <t> -vframes 1 f.png`) and inspect them (vision). Verify: panel/content actually
   visible, no blocking overlays (e.g. "Stop sharing" banners), success states not failure states
   (a red FAIL badge in frame = re-record). Fix root causes, then re-record. Never ship unseen footage.

## Pitfalls

- **Fix visible app breakage BEFORE recording**, not during editing. Users notice broken UI in
  videos instantly ("the site is broken") — and they may mean a different surface than you assume;
  ask or screenshot each candidate surface rather than guessing.
- **Make test data collision-proof per take** (unique phones/dates/order ids per run) so a prior
  manual test can't turn the recorded baseline into a duplicate-rejection failure.
- Recording captures everything on the shared browser surface — close stray tabs, settle event
  feeds, and let animations warm up before the first narration beat.
- If narration is regenerated, RE-TIME all recording beats to the new track before re-recording.

## Files

- `references/webcmd-headless-recording.md` — capture mechanics via webcmd CLI: session pattern,
  QuickJS sandbox rules, the evaluate()-args escaping rule, getDisplayMedia/MediaRecorder recipe,
  chunked blob extraction, ffmpeg mux.
