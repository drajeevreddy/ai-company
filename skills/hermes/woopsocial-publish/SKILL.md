---
name: woopsocial-publish
description: Use when publishing or scheduling posts via WoopSocial.
---

# Publishing through WoopSocial

Use when a post must actually go live on a connected social account (Instagram, X, LinkedIn,
LinkedIn Pages, Facebook, Threads, Pinterest, TikTok, YouTube) instead of being drafted.

## Order of operations

1. `social_accounts_list` and `projects_list` — get the `socialAccountId` and `projectId`. All accounts
   on one post must share a project.
2. Per file: `media_uploads_create_session` with `projectId` + `fileSizeInBytes`. Returns
   `uploadSessionId`, `partSizeInBytes` (10 MB), `partCount` and one presigned `uploadUrl` per part.
3. Upload the bytes with curl, not the MCP client:
   `curl -sS -o /dev/null -w '%{http_code}' -X PUT --data-binary @file -H 'Content-Type: application/octet-stream' "$URL"`
   Every part except the last must be exactly `partSizeInBytes`.
4. `media_uploads_complete_session` with `uploadSessionId` — returns `mediaId` once status is `READY`.
5. `posts_validate` with the exact final payload, then `posts_create` with the same payload.

## Payload shape

```json
{
  "content": [{"text": "caption", "media": [{"type": "MEDIA_LIBRARY", "mediaId": "..."}]}],
  "schedule": {"type": "PUBLISH_NOW"},
  "socialAccounts": [{"platform": "INSTAGRAM", "postType": "POST", "socialAccountId": "..."}]
}
```

- Carousel = several media entries inside the single `content[0].media` array, in display order.
- Instagram `postType`: `POST` (feed, images and carousels), `REEL`, `STORY`.
- `schedule`: `DRAFT`, `PUBLISH_NOW`, or `SCHEDULE_FOR_LATER` with `scheduledFor` as **UTC** ISO 8601.
  For IST 19:00 send `13:30:00Z` the same day.
- `content` takes exactly one item today. Threads are not supported yet.

## Verifying a publish

`posts_create` returns `deliveryStatus: NOT_STARTED`. Re-read with `posts_get` until it is
`PUBLISHED` (usually inside two minutes) and report `externalPostUrl`. Do not call the work done on the
create response alone — `FAILED` carries the reason in the same record.

## Gotchas

- Media ids live in the library after publishing unless `autoDeleteMediaAfterPublish: true`.
- Feed images must be 4:5 or better; 1080x1350 is the safe canvas.
- **Music is not reachable by any automated route.** Instagram's web uploader has no music picker and its
  API publishes silent. Music is app-only, chosen at compose time, and cannot be added after publishing.
  If a post needs a song, it ships from the phone, not from here.
- Browser automation is the wrong tool for Instagram carousels: the composer's file input is
  `multiple`, and a single-path attach tool cannot fill it, so only one image per post gets through.
  Use WoopSocial for anything with more than one image.
- The MCP client here refuses batched local tool calls; issue one `tool_call` per WoopSocial call.
