# Generic IMAP + SMTP Template

Copy this into `~/.config/himalaya/config.toml` and fill in your values.

## Implicit TLS (port 993/465)

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

## STARTTLS variant (port 587)

Replace the SMTP line with:

```toml
smtp.server = "smtp://smtp.example.com:587"
smtp.starttls = true
```

## Secure password (recommended for production)

Replace `password.raw` with:

```toml
imap.sasl.plain.password.command = "pass show email/imap"
smtp.sasl.plain.password.command = "pass show email/smtp"
```

## SASL LOGIN (instead of PLAIN)

Some servers require LOGIN instead of PLAIN:

```toml
imap.sasl.login.username = "you@example.com"
imap.sasl.login.password.raw = "your-password"
```

## Test

```bash
himalaya mailbox list --log-level debug
```