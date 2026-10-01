# Zoho Mail Configuration

## Template

```toml
[accounts.zoho]
default = true
email = "you@yourdomain.in"
display-name = "Your Name"

imap.server = "imaps://imap.zoho.in:993"
imap.sasl.plain.username = "you@yourdomain.in"
imap.sasl.plain.password.raw = "your-password"

smtp.server = "smtps://smtp.zoho.in:465"
smtp.sasl.plain.username = "you@yourdomain.in"
smtp.sasl.plain.password.raw = "your-password"

mailbox.alias.inbox = "INBOX"
mailbox.alias.sent = "Sent"
mailbox.alias.drafts = "Drafts"
mailbox.alias.trash = "Trash"
```

For Zoho India use `zoho.in` servers. For other regions: `zoho.com`, `zoho.eu`, `zoho.com.au`, etc.

## Zoho IMAP Troubleshooting

Zoho rejects IMAP with `You are yet to enable IMAP for your account` even when
the admin panel says everything is enabled. Check all three levels:

### 1. Org-level (admin console)
admin.zoho.in → Mail Settings → Security Policies → IMAP Access → ON

### 2. User-level (personal mail settings)
mail.zoho.in → Settings (gear icon) → Mail Accounts → your account → "Enable IMAP" toggle

This is the most commonly missed one. The admin console "Configurations" page
is just reference info (server names/ports) — it does NOT control IMAP access.

### 3. App Password (if 2FA is enabled)
mail.zoho.in → Settings → Security → App Passwords → Generate for "Mail"
Use the generated password, not your login password.

### Username format
Always use full email: `you@yourdomain.in` (not just `you`). Without the domain,
Zoho returns `Invalid credentials` instead of `IMAP not enabled`.

## Test

```bash
himalaya mailbox list --log-level debug
```

If you see `AUTHENTICATE PLAIN failed: NO` — one of the three levels above is off.

## Raw IMAP test (bypass himalaya)

```bash
echo -e "a1 LOGIN you@yourdomain.in your-password\na2 LOGOUT" | openssl s_client -connect imap.zoho.in:993 -quiet 2>/dev/null
```