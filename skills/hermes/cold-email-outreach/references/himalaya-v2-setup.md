# Himalaya v2.x Setup Reference

## Config File Location

`~/.config/himalaya/config.toml`

## v2.x Config Format

v2.x uses flat dotted keys with URL-format server addresses. The old v1.x `backend.type`/`backend.host`/`backend.port`/`backend.encryption.type` syntax does NOT work.

### Generic Template

```toml
[accounts.NAME]
email = "you@example.com"
display-name = "Your Name"
default = true

# IMAP — imaps:// for implicit TLS (port 993)
imap.server = "imaps://imap.example.com:993"
imap.sasl.plain.username = "you@example.com"
imap.sasl.plain.password.raw = "your-password"
# or: imap.sasl.plain.password.command = "pass show email/imap"

# SMTP — smtps:// for implicit TLS (port 465)
smtp.server = "smtps://smtp.example.com:465"
smtp.sasl.plain.username = "you@example.com"
smtp.sasl.plain.password.raw = "your-password"
# or: smtp.sasl.plain.password.command = "pass show email/smtp"

# Mailbox aliases (singular in v2.x)
mailbox.alias.inbox = "INBOX"
mailbox.alias.sent = "Sent"
mailbox.alias.drafts = "Drafts"
mailbox.alias.trash = "Trash"
```

### Provider: Zoho Mail

```toml
[accounts.zoho]
email = "you@yourdomain.com"
display-name = "Your Name"
default = true

imap.server = "imaps://imap.zoho.in:993"
imap.sasl.plain.username = "you@yourdomain.com"
imap.sasl.plain.password.raw = "your-password"

smtp.server = "smtps://smtp.zoho.in:465"
smtp.sasl.plain.username = "you@yourdomain.com"
smtp.sasl.plain.password.raw = "your-password"

mailbox.alias.inbox = "INBOX"
mailbox.alias.sent = "Sent"
mailbox.alias.drafts = "Drafts"
mailbox.alias.trash = "Trash"
```

**Zoho regions:**
- India: `imap.zoho.in` / `smtp.zoho.in`
- US: `imap.zoho.com` / `smtp.zoho.com`
- EU: `imap.zoho.eu` / `smtp.zoho.eu`
- Australia: `imap.zoho.com.au` / `smtp.zoho.com.au`

**Zoho requirement:** IMAP and SMTP must be enabled in the web interface (Settings → Mail Accounts → [account] → IMAP Access / SMTP). Without this, auth fails with `NO You are yet to enable IMAP for your account`.

### Provider: Gmail

```toml
[accounts.gmail]
email = "you@gmail.com"
display-name = "Your Name"
default = true

imap.server = "imaps://imap.gmail.com:993"
imap.sasl.plain.username = "you@gmail.com"
imap.sasl.plain.password.command = "pass show google/app-password"

smtp.server = "smtps://smtp.gmail.com:465"
smtp.sasl.plain.username = "you@gmail.com"
smtp.sasl.plain.password.command = "pass show google/app-password"

# Gmail folder mapping — required, otherwise save-to-Sent fails
mailbox.alias.inbox = "INBOX"
mailbox.alias.sent = "[Gmail]/Sent Mail"
mailbox.alias.drafts = "[Gmail]/Drafts"
mailbox.alias.trash = "[Gmail]/Trash"
```

**Gmail requires an App Password** if 2FA is enabled.

### Provider: iCloud

```toml
[accounts.icloud]
email = "you@icloud.com"
display-name = "Your Name"

imap.server = "imaps://imap.mail.me.com:993"
imap.sasl.plain.username = "you@icloud.com"
imap.sasl.plain.password.command = "pass show icloud/app-password"

smtp.server = "smtps://smtp.mail.me.com:465"
smtp.sasl.plain.username = "you@icloud.com"
smtp.sasl.plain.password.command = "pass show icloud/app-password"
```

**Note:** Generate an app-specific password at appleid.apple.com

## Verification After Config Change

Always run after editing config.toml:

```bash
himalaya mailbox list
himalaya envelope list --page-size 1
```

If these fail, the config has issues — fix before proceeding to sending.

## v1.x to v2.x Migration

| v1.x key | v2.x key |
|---|---|
| `backend.type = "imap"` | Use `imap.server` with URL scheme |
| `backend.host` | Included in `imap.server` URL |
| `backend.port` | Included in `imap.server` URL |
| `backend.encryption.type` | URL scheme: `imaps://` = TLS, `imap://` = plain |
| `backend.login` | `imap.sasl.plain.username` |
| `backend.auth.raw` | `imap.sasl.plain.password.raw` |
| `backend.auth.cmd` | `imap.sasl.plain.password.command` |
| `message.send.backend.*` | `smtp.*` (same pattern as IMAP) |
| `folder.aliases.X` (plural) | `mailbox.alias.X` (singular) |