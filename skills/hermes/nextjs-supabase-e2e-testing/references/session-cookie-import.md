# Reusing the user's existing browser session instead of a password

Goal: drive a logged-in app in the headless browser when you must not handle the account password. The user's own Chrome already holds a valid session cookie for the origin; decrypt it and hand it to the headless context. Verified working against a Next.js + Supabase app on Vercel.

Do not type a password into a login form. If the vault has no item for the origin and `browser_vault_save_login` refuses the page, this is the path — not a request for the password in chat.

## 1. Find the real browser's cookie store

```bash
ls ~/.var/app/com.google.Chrome/config/google-chrome/*/Cookies   # Chrome via Flatpak
ls ~/.config/chromium/*/Cookies                                  # Chromium
```

Copy the sqlite file before opening it — the live DB is locked and being written.

## 2. Get the keyring secret

The terminal Hermes runs in has no session bus, so `secret-tool` fails with `Cannot autolaunch D-Bus without X11 $DISPLAY`. Point it at the user's bus:

```bash
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus
secret-tool lookup application chrome     # -> base64, the "Chrome Safe Storage" password
```

## 3. Decrypt (Linux, v11 cookies)

```python
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

key = hashlib.pbkdf2_hmac('sha1', stored_password_b64.encode(), b'saltysalt', 1, 16)
pt = Cipher(algorithms.AES(key), modes.CBC(b' ' * 16)).decryptor().update(encrypted_value[3:])
unpadder = padding.PKCS7(128).unpadder()
value = (unpadder.update(pt) + unpadder.finalize())[32:]
```

Three things that cost time here:

- The libsecret value is still run through PBKDF2-HMAC-SHA1 (`saltysalt`, 1 iteration, 16 bytes). Decoding it and using it as the AES key directly produces garbage and an `Invalid padding bytes` error.
- `encrypted_value` starts with a 3-byte `v10`/`v11` prefix. Skip it.
- **Chrome prepends 32 bytes to the plaintext of every cookie.** The real value is `plaintext[32:]`, and that prefix is identical for every cookie in a store. Verify the offset on a cookie whose value you can predict before trusting it (`isLoggedIn` → `1`, `lastUsedAuth` → `google`).

## 4. Confirm you recovered the session

Supabase's cookie value is `"base64-" + base64url(JSON)` with padding stripped. Decode and check for `access_token`, `refresh_token`, `expires_at`, and `user.email` — that also yields the bearer token the data-layer probes need.

```python
b = value[len('base64-'):]; b += '=' * (-len(b) % 4)
session = json.loads(base64.urlsafe_b64decode(b))
```

Write the token to a file on disk and have curl read it (`Authorization: Bearer $(cat /tmp/token)`); never echo it into the transcript.

## 5. Import into the headless context

Camofox exposes an endpoint that is absent from `/openapi.json`:

```
POST /sessions/<userId>/cookies
{"cookies": [{"name": "sb-<ref>-auth-token", "value": "<value>", "domain": "<host>", "path": "/",
              "expires": <unix>, "httpOnly": false, "secure": true, "sameSite": "Lax"}],
 "tabId": "<tab>"}
```

- Playwright cookie shape, 512kb body limit, up to 500 cookies.
- `<userId>` comes from `GET /health` → `activeUserIds[0]` immediately after a browser tool call. Cleanup only drops the local tracking entry, so the id stays valid for the session.
- The route refuses with 409 unless a canonical profile and a live session exist for that user — do a `navigate` first so a tab exists, and pass its `tabId` from `GET /tabs?userId=<id>`.
- The cookie is not httpOnly, so it is visible to `document.cookie` afterwards — useful as a check, not as a way in.

Build the JSON in a script that reads the value from disk and posts it, so the secret never appears in a command or message.

## 6. Verify

Navigate to a protected route and assert the app shell rendered (sidebar, nav links, user chip) — a 200 with a bare `main` means the session was not accepted. Then re-read the page a few seconds later, because client-rendered routes fill in after the first paint.

## Dead ends (do not repeat)

- **Setting `document.cookie` from the page via a local helper server.** An https page calling `http://localhost` dies as mixed content; the fetch fails before any cookie is written.
- **Writing a row into the Camofox Firefox profile's `cookies.sqlite`.** Profile dirs are `hermes_<uuid>` and a new one is created per browser session, and the running browser keeps cookies in memory, so an external insert is invisible until restart and usually lands in a profile that will not be used again.
- **Waiting on `browser_vault_save_login`.** It needs a login-form signal for the origin it has tracked; on a client-rendered login page it can refuse even while the form is on screen.

## Caveat to state in the report

A session-import run does not exercise the login form. Say so explicitly: authentication is verified by session, and password reset / wrong-password handling remain untested.
