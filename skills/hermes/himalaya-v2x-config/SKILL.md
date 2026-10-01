---
name: himalaya-v2x-config
description: "Himalaya v2.x config templates for IMAP/SMTP providers."
version: 1.0.0
author: painarise
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Email, IMAP, SMTP, CLI, Himalaya, Config]
    homepage: https://github.com/pimalaya/himalaya
prerequisites:
  commands: [himalaya]
---

# Himalaya v2.x Configuration

Himalaya v2.1.0+ uses a different config format than v1.x. The main himalaya skill documents v1.x syntax which is obsolete for current installs.

## Procedure

1. Check `himalaya --version` — if v2.x, use the flat dotted key format below
2. Copy the appropriate template from `templates/` for your provider
3. Fill in credentials
4. Test with `himalaya mailbox list --log-level debug`
5. If you get `No backend matching auto is configured`, you wrote v1.x config for v2.x — rewrite

## v2.x Config Format

```toml
[accounts.yourname]
default = true
email = "you@example.com"
display-name = "Your Name"

imap.server = "imaps://imap.example.com:993"
imap.sasl.plain.username = "you@example.com"
imap.sasl.plain.password.raw = "your-password"

smtp.server = "smtps://smtp.example.com:465"
smtp.sasl.plain.username = "you@example.com"
smtp.sasl.plain.password.raw = "your-password"

mailbox.alias.inbox = "INBOX"
mailbox.alias.sent = "Sent"
mailbox.alias.drafts = "Drafts"
mailbox.alias.trash = "Trash"
```

For password from command: `imap.sasl.plain.password.command = "pass show email/imap"`
For STARTTLS: use `smtp://host:587` scheme instead of `smtps://host:465`

## Key Differences from v1.x

| v1.x | v2.x |
|------|------|
| `backend.type = "imap"` | removed |
| `backend.host = "host"` | `imap.server = "imaps://host:993"` |
| `backend.port = 993` | embedded in URL |
| `backend.encryption.type = "tls"` | scheme `imaps://` |
| `backend.auth.raw = "pass"` | `imap.sasl.plain.password.raw = "pass"` |
| `folder.aliases.sent = "Sent"` | `mailbox.alias.sent = "Sent"` |

## References

- `templates/generic-imap-smtp.md` — generic IMAP+SMTP template
- `templates/zoho-mail.md` — Zoho Mail with gotchas
- `templates/gmail.md` — Gmail with folder mapping