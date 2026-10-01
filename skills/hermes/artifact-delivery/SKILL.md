---
name: artifact-delivery
description: Use when delivering a file or report to the user's chat.
version: 1.0.0
author: hermes-curator
license: MIT
metadata.hermes.tags: [telegram, delivery, notifications, attachments, gateway]
metadata.hermes.related_skills: [himalaya]
---

# Artifact delivery — getting the deliverable onto the user's device

An audit, report, chart or PDF that stays on disk has not been delivered. When the
user says "send it to me", "deliver this", or "put it on my phone", the task is not
done until it is on a channel they actually read.

## When to Use

- The user asks for a produced file or a summary to be sent to their chat/phone.
- You finished a report and the natural close is "here it is on your device".
- A long-running job finished and the user expected a notification.
- You want to verify a delivery actually landed rather than assuming it did.

## 1. Find the channel and credential

The Hermes env file carries the platform credentials. Read the *names* first, never
dump the values:

```bash
grep -i "telegram\|whatsapp\|discord" ~/.hermes/.env | sed 's/=.*/=<redacted>/'
```

Typical keys: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_HOME_CHANNEL` (the chat id),
`TELEGRAM_ALLOWED_USERS`. The home channel is usually the user's own DM — that is
the default target unless they name another.

Confirm the bot is live before sending anything, otherwise a wrong token looks like
a delivery failure later:

```bash
curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe" \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('ok'), d.get('result',{}).get('username'))"
```

## 2. Send: summary message first, then the file

Send the **summary as a message** and the **artifact as a document**. A bare file
with no context makes the user open it to find out what it is; a bare message with
no file makes them ask for it.

```python
import json, subprocess
# load token + chat from ~/.hermes/.env into `tok` / `chat` (skip commented lines)

def tg(method, fields=None, files=None):
    url = f"https://api.telegram.org/bot{tok}/{method}"
    cmd = ["curl", "-s", "-o", "/tmp/tg_resp.json", url]
    if files:
        for f in files:
            cmd += ["-F", f]
    else:
        for k, v in fields.items():
            cmd += ["--data-urlencode", f"{k}={v}"]
    subprocess.run(cmd, capture_output=True, text=True)
    return json.load(open("/tmp/tg_resp.json"))
```

- `sendMessage` with `chat_id` + `text` — cap **4096** chars. Split longer digests.
- `sendDocument` with `chat_id` + `document=@/abs/path` — caption cap **1024** chars.
- Send the file **by absolute path**; the working directory is not guaranteed.

**Drop `parse_mode` for a Telegram digest.** The MarkdownV2 escape set is brutal
and silently 400s on characters that appear constantly in audit prose (`-`, `.`,
`(`, `!`, `#`). Plain text with ordinary line breaks renders correctly on mobile and
never fails to send. Use Markdown only when the formatting is worth the escaping.

## 3. Verify the delivery — do not assume it landed

A `curl` that exits 0 proves nothing. Check the API response:

```python
r = tg("sendDocument", None, [f"chat_id={chat}", f"document=@{path}"])
assert r.get("ok") is True
assert r["result"]["document"]["file_size"] == os.path.getsize(path)
```

- `ok: true` plus a real `message_id` is the acknowledgement.
- **`file_size` matching the on-disk size byte for byte is the proof** the whole
  file went, not a truncated upload.
- A non-`ok` response carries `description` — read it ("chat not found", "file is
  too big", "bot was blocked by the user") rather than retrying blindly.

Report the delivery with the message ids and the verified size. That converts
"I sent it" into a fact the user can check.

## 4. What to send

Match the channel. A phone digest should be:

- **Verdict first**, then the handful of highest-priority items — not the full
  report pasted into a message.
- **Counts and names**, not prose paragraphs.
- **The file attached** for anything long, with the path in the workspace as
  well so it can be found later from a terminal.

Send both a human-readable rendering (PDF) and the edit-ready source (`.md`) when
the artifact is meant to be handed to another agent — the PDF to read, the source
to execute.

## Pitfalls

- **Never print or echo the token.** Use a variable, and redirect curl's output to
  a file so an error cannot dump the request URL (which contains the token). To show
  the response, print only the parsed JSON body.
- **`--data-urlencode`, not string interpolation**, for message text. A digest
  containing `&`, `"`, or newlines will otherwise truncate or corrupt the payload.
- **A cron job scheduled from an interactive CLI session does not deliver back into
  that session.** If the user wants a notification, set the job's delivery target to
  a gateway-connected platform explicitly — check the job's `deliver` field rather
  than assuming the default reaches them.
- **Confirm the target channel.** The home channel is the user's DM by default; if
  they name a group or a specific thread, use that exact id including any thread
  component.
- **Retry once on a transient network error, not forever.** A repeated `ok: false`
  with the same `description` is a real refusal (blocked bot, wrong id) — report it
  instead of looping.

## Related

- `himalaya` for email delivery over IMAP/SMTP.
