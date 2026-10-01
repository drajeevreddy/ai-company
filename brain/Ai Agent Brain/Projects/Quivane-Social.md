# Quivane — social

The owner's agency. Instagram `@quivaneofficial` ("Quivane | Strategy & Execution"), site quivane.in.

## Where things live

| What | Path |
|---|---|
| Agent workspace, all briefs and approved copy | `/home/painarise/Music/Social Media Auto/` |
| Brand source of truth (owner-ruled) | `.../quivane-brand-facts.md` |
| Approved copy, frozen | `.../quivane-apollo-drafts.md` |
| Finished post set (images + captions) | `/home/painarise/Quivane-Next-Week/` |
| Published carousel template, the design reference | `/home/painarise/Downloads/quivane_instagram_1..6_full_logo.png` |
| Product used as proof on the reel | `/home/painarise/Documents/Projects/Quivane OS/` |
| Identity note | `/home/painarise/quivane-identity.md` |

## Canvas

October workspace, nodes named Orion (Hermes, coordinator) → Apollo (opencode, copy) → Juno
(Antigravity, design) → Athena (opencode, publishing) → browser. `message_peer` only reaches
directly-connected peers, so Orion can message Apollo alone; use `send_to_node` with the node id to
reach Juno and Athena. See the `october-canvas-bus` skill.

## Brand rules that are not negotiable

Owner-ruled 14 Sep 2026, all recorded in the brand file:

- **Palette is the logo, not the identity note.** Accent `#E0010F` red on `#FBF9F9`; ink `#0A0A0B`.
  `quivane-identity.md` specifies orange `#FF5B2E` on near-black and is superseded for social.
- **No statistics about the agency.** The feed carries two contradictory sets (40+/12+/98% vs
  100+/50+/10+) and neither is sourced. Nothing numeric ships until a real written source exists.
- **No slogan line.** Retired: "Strategy • Execution • Impact", "Think. Build. Execute.", and
  "We tailor. We build. We deliver." (the third was live on the published carousel and had been missed).
- **One CTA, everywhere:** `quivane.in in bio.`
- **Posting window 18:30–20:00 IST.** The first nine posts went out 21:55–00:31 IST, hand-posted.
- **Technology may be named only if it appears in our own repos.** TypeScript, Next.js, Postgres,
  Docker are verifiable. There is no Python service, no FastAPI, no Django, no Flask on the machine.

## Design system, measured off the published carousel

Visual language now has two layers: the published carousel measured below, and
[[Projects/Quivane-Design-System]], measured 15 Sep 2026 off `/home/painarise/Pictures/INSPO`
(tighter 4.2–4.6% outer margin, `#D30000` red on `#FEFEFE`). The `quivane-design-system` skill
loads the INSPO set, which is the newer, denser one.

Not invented — sampled from `quivane_instagram_*_full_logo.png`: left margin 128, top rail 56,
logo rail ~72 tall, headline 96–128px, body 38px, line pitch ≈1.0em, page indicator top-right,
one accent hairline under the heading. 1080×1350 feed, 1080×1920 reel.

Generator: `/home/painarise/Music/Social Media Auto/build_quivane_week.py` (Pillow, Montserrat +
Adwaita Mono, since Inter and JetBrains Mono are not installed).

## Publishing, live as of 15 Sep 2026

Publishing is **automated now**: the WoopSocial MCP publishes to Instagram. Account
`quivaneofficial` = social account id `173300581098586112`, project `173300143959834624`.
X `@Quivaneofficial` is connected to the same project.

Flow: `media_uploads_create_session` (projectId + byte size) → `curl -X PUT --data-binary @file` to the
presigned part URL → `media_uploads_complete_session` → `posts_create` with
`schedule.type = PUBLISH_NOW` or `SCHEDULE_FOR_LATER` (UTC ISO). Media must be 1080×1350 for a feed
carousel; images stay in the library unless `autoDeleteMediaAfterPublish` is set.

**No music path exists on either route.** Instagram's web uploader has no music picker and its API
publishes silent. Music on a feed post is app-only, added at compose time, and cannot be added after
publishing. The seven `song.txt` files carry the picks for a phone post if that ever matters.

Post 1 of the seven-day set published 15 Sep 2026 14:21 IST:
https://www.instagram.com/p/DdTUp46FalE/ (postId `173354782235295744`, external `18390418951204354`).

## Open with the owner

- **Publishing is automated as of 15 Sep 2026** (WoopSocial, see above). The scheduler question is settled: it is WoopSocial's, and times are passed as UTC ISO.
- **The 15–21 Sep seven-day set is a new set** at `/home/painarise/Quivane-7-Day/` and supersedes the
  older `~/Quivane-Next-Week/` folder for scheduling. Its day 1 is PUBLISHED (link above). Days 2–7 are
  built, verified and waiting on a go.
- **Codex image generation is out of quota** until Oct 12 2026 12:49. Two slides were made with it and
  are word-perfect; the rest of the set is type-rendered instead. Re-render with Codex after that date and
  swap the images, keeping the same captions.
- **Nothing else is scheduled.** The old set's posts 1, 2, 4, 5 are READY-FOR-APPROVAL only and are
  superseded. Post 3 of the old set stays blocked on a real 20–30-second Quivane OPS screen recording.
- **Proposed run, pending explicit per-post approval:** posts 1–5 in sequence, Mon 21 through Fri 25 Sep 2026 at 19:00 IST. If post 3's recording misses Wednesday, hold it or move it after post 5—do not delay the other ready posts.
- Which screen the reel records (fleet strip, approval queue, or terminal pane).
- Whether Python or FastAPI is used anywhere, which would restore them to the stack post.
- Whether any real client engagements exist on file, which would restore the number claims.
