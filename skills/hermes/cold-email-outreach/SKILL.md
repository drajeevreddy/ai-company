---
name: cold-email-outreach
description: "Send cold emails via Himalaya CLI. Compose, send, track."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Email, Cold-Email, Outreach, Himalaya, SMTP]
    requires_commands: [himalaya]
---

# Cold Email Outreach

Send cold emails to business owners from the terminal using Himalaya CLI. Covers the end-to-end workflow: account setup, email composition, batch sending, and deliverability hygiene.

## Prerequisites

- Himalaya v2.x installed and configured (see `references/himalaya-v2-setup.md` for the v2.x config format)
- A configured email account in `~/.config/himalaya/config.toml`
- IMAP/SMTP enabled on the provider's web interface (required for Zoho, Outlook, etc.)

## Procedure

### 1. Verify the email account works

Always verify before sending anything:

```bash
himalaya mailbox list
himalaya envelope list --page-size 1
```

If this fails, fix the config first — do not proceed to sending.

### 2. Compose the email

Use piped input for non-interactive sending from Hermes:

```bash
cat << 'EOF' | himalaya template send
From: Rajeev Reddy <rajeevreddy@quivane.in>
To: recipient@business.com
Subject: Your Subject Here

Email body here.
EOF
```

**Always include the From header** — without it, the sender address may be wrong or missing.

### 3. Send and verify

After sending, check the Sent folder to confirm delivery:

```bash
himalaya envelope list --mailbox "Sent" --page-size 1
```

If the send command fails but the email appears in Sent, SMTP succeeded and the failure was only the save-to-Sent step. Do NOT retry — that sends a duplicate.

### 4. Track what was sent

For cold outreach, maintain a simple log (CSV or markdown) of:
- Recipient email
- Subject line
- Date sent
- Follow-up status

This prevents duplicate outreach and enables follow-up sequences.

## Pitfalls

- **Zoho IMAP/SMTP not enabled:** Zoho returns `NO You are yet to enable IMAP for your account` until IMAP is toggled on in the web interface (Settings → Mail Accounts → [account] → IMAP Access). Always verify `himalaya mailbox list` works before attempting to send.
- **SMTP success + save-to-Sent failure = duplicate risk:** If `himalaya template send` exits non-zero but the email appears in Sent, the email was delivered. Do not retry.
- **Gmail daily limits:** Free Gmail caps at ~500 emails/day, Workspace at ~2000. Cold email at scale needs a dedicated service (SendGrid, Mailgun, Amazon SES).
- **v1.x vs v2.x config syntax:** Himalaya v2.x uses `imap.server`, `smtp.server`, `imap.sasl.plain.username`, etc. The old `backend.type`/`backend.host`/`backend.port` syntax silently fails with "No backend matching `auto` is configured".
- **Mailbox alias syntax changed:** v2.x uses `mailbox.alias.X` (singular), not `folder.aliases.X` (plural). The old form is silently ignored, causing save-to-Sent failures on Gmail.

## User Preferences

- User prefers concise, direct communication — no filler or restating.
- Email account: rajeevreddy@quivane.in via Zoho Mail.
- Use piped input for sending, not interactive editor mode.

## Verification

- [ ] `himalaya mailbox list` succeeds before any send attempt.
- [ ] Each sent email is verified in the Sent folder.
- [ ] No duplicate sends on retry after SMTP success.
- [ ] A send log tracks recipients, subjects, and dates.