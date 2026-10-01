#!/usr/bin/env python3
"""Import an existing browser session cookie into the live Camofox context.

Use when you must drive a logged-in app headlessly and must not handle the account
password. Decrypts the cookie from the user's real Chrome/Chromium store (Linux,
v10/v11) and posts it to Camofox's POST /sessions/<userId>/cookies.

Prereqs:
  export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus   # secret-tool
  pip install cryptography

Usage:
  python3 import_browser_session_cookie.py \
      --origin endocare-gold.vercel.app \
      --cookie-name sb-cnsuyhmtbqdxsxloyljq-auth-token \
      --cookies-db ~/.var/app/com.google.Chrome/config/google-chrome/Default/Cookies

The userId/tabId are discovered from the running Camofox server; run a browser tool
call first so the session exists. Nothing secret is printed to the transcript.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

CAMOFOX = "http://localhost:9377"


def get_keyring_password() -> str:
    out = subprocess.run(
        ["secret-tool", "lookup", "application", "chrome"],
        capture_output=True, text=True, timeout=30,
    )
    if out.returncode != 0 or not out.stdout.strip():
        sys.exit("secret-tool failed — export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$(id -u)/bus")
    return out.stdout.strip()


def decrypt(encrypted: bytes, password: str) -> bytes:
    """Linux v10/v11: PBKDF2-HMAC-SHA1(saltysalt,1,16) + AES-128-CBC, IV = 16 spaces.
    Chrome prepends 32 bytes to the plaintext of every cookie — strip them."""
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.primitives import padding

    key = hashlib.pbkdf2_hmac("sha1", password.encode(), b"saltysalt", 1, 16)
    body = encrypted[3:]  # drop the b'v10'/b'v11' prefix
    pt = Cipher(algorithms.AES(key), modes.CBC(b" " * 16)).decryptor().update(body)
    unpadder = padding.PKCS7(128).unpadder()
    plain = unpadder.update(pt) + unpadder.finalize()
    return plain[32:]


def read_cookie(db: str, host: str, name: str, password: str) -> str:
    # Copy first: the live store is locked and being written.
    tmp = Path(tempfile.mkdtemp()) / "Cookies"
    shutil.copy(db, tmp)
    con = sqlite3.connect(tmp)
    row = con.execute(
        "select encrypted_value from cookies where host_key=? and name=?", (host, name)
    ).fetchone()
    con.close()
    if not row:
        sys.exit(f"no cookie {name!r} for {host!r} in {db} — is that profile signed in?")
    return decrypt(row[0], password).decode("utf-8", "replace")


def api(path: str, payload=None, method="GET"):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(CAMOFOX + path, data=data, method=method,
                                headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def decode_supabase_session(value: str) -> dict:
    b = value[len("base64-"):] if value.startswith("base64-") else value
    b += "=" * (-len(b) % 4)
    return json.loads(base64.urlsafe_b64decode(b).decode())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--origin", required=True, help="cookie host, e.g. app.vercel.app")
    ap.add_argument("--cookie-name", required=True, help="e.g. sb-<ref>-auth-token")
    ap.add_argument("--cookies-db", required=True, help="path to the Chrome/Chromium Cookies sqlite")
    ap.add_argument("--user-id", help="Camofox userId; discovered from /health when omitted")
    ap.add_argument("--tab-id", help="Camofox tabId; discovered from /tabs when omitted")
    ap.add_argument("--token-out", default="/tmp/api_token.txt",
                    help="where to write the access_token for the data-layer probes")
    args = ap.parse_args()

    health = api("/health")
    user_id = args.user_id or (health.get("activeUserIds") or [None])[0]
    if not user_id:
        sys.exit("no active Camofox user — call a browser tool once, then rerun")

    tabs = api(f"/tabs?userId={user_id}").get("tabs", [])
    tab_id = args.tab_id or (tabs[-1]["tabId"] if tabs else None)
    if not tab_id:
        sys.exit("no live tab for that user — navigate somewhere first, then rerun")

    value = read_cookie(args.cookies_db, args.origin, args.cookie_name, get_keyring_password())

    if value.startswith("base64-"):
        session = decode_supabase_session(value)
        Path(args.token_out).write_text(session["access_token"])
        print(f"access_token written to {args.token_out} "
              f"(user={session['user']['email']}, expires_at={session.get('expires_at')})")

    res = api(f"/sessions/{user_id}/cookies", {
        "cookies": [{
            "name": args.cookie_name,
            "value": value,
            "domain": args.origin,
            "path": "/",
            "expires": int(time.time()) + 7 * 86400,
            "httpOnly": False,
            "secure": True,
            "sameSite": "Lax",
        }],
        "tabId": tab_id,
    }, method="POST")
    print(f"imported: {res} (value length {len(value)}, not printed)")
    print("now navigate to a protected route and assert the app shell renders")


if __name__ == "__main__":
    main()
