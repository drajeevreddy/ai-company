# Gmail Configuration

## Template

```toml
[accounts.gmail]
default = true
email = "you@gmail.com"
display-name = "Your Name"

imap.server = "imaps://imap.gmail.com:993"
imap.sasl.plain.username = "you@gmail.com"
imap.sasl.plain.password.command = "pass show google/app-password"

smtp.server = "smtps://smtp.gmail.com:465"
smtp.sasl.plain.username = "you@gmail.com"
smtp.sasl.plain.password.command = "pass show google/app-password"

# Gmail folder mapping — REQUIRED or save-to-Sent fails
mailbox.alias.inbox = "INBOX"
mailbox.alias.sent = "[Gmail]/Sent Mail"
mailbox.alias.drafts = "[Gmail]/Drafts"
mailbox.alias.trash = "[Gmail]/Trash"
```

## App Password

Gmail requires an App Password when 2FA is enabled (and it should be).
Generate at: myaccount.google.com → Security → App passwords → select "Mail"

## Sending Limits

- Free Gmail: ~500 emails/day
- Google Workspace: ~2,000/day
- Cold email gets flagged fast — use a dedicated service for outreach

## Test

```bash
himalaya mailbox list --log-level debug
```