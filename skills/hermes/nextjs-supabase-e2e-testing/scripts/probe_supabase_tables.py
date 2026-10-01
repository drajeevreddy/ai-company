#!/usr/bin/env python3
"""Probe a Supabase project for which tables exist, which hold rows, and what an
anonymous caller can reach. Run this BEFORE any data-layer verdict: page names are
not table names, and 'the table is empty' and 'RLS hid everything' look identical.

Usage:
  SUPABASE_URL=https://<ref>.supabase.co \
  ANON_KEY=$(cat /tmp/anon_key.txt) TOKEN=$(cat /tmp/api_token.txt) \
  python3 probe_supabase_tables.py [extra candidate ...]

Output per table: status, authenticated row count, and the PGRST205 hint when the
name is wrong — the hint names the real table.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

BASE = os.environ["SUPABASE_URL"].rstrip("/")
ANON = os.environ["ANON_KEY"].strip()
TOKEN = (os.environ.get("TOKEN") or "").strip() or ANON

DEFAULT_CANDIDATES = [
    "profiles", "clinics", "doctors", "patients", "appointments", "queue", "consultations",
    "soap_notes", "prescriptions", "prescription_items", "medicines", "lab_orders", "lab_tests",
    "lab_results", "invoices", "invoice_items", "payments", "reminders", "auto_reminder_logs",
    "patient_documents", "patient_allergies", "activity_logs", "clinic_settings", "roles",
]


def get(path: str, token: str):
    req = urllib.request.Request(BASE + path)
    req.add_header("apikey", ANON)
    req.add_header("Authorization", "Bearer " + token)
    req.add_header("Prefer", "count=exact")
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, r.read().decode(), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(), dict(e.headers)


def probe(name: str) -> str:
    st, body, headers = get(f"/rest/v1/{name}?select=*&limit=1", TOKEN)
    if st != 200:
        try:
            hint = json.loads(body).get("hint") or ""
        except Exception:
            hint = ""
        return f"MISSING  hint: {hint[:90]}"
    rows = json.loads(body)
    rng = headers.get("Content-Range", "?")
    count = rng.split("/")[-1] if "/" in rng else "?"
    if not rows:
        return f"EMPTY (authenticated count={count}) — an anon 200 [] here proves nothing"
    return f"HAS ROWS (authenticated count={count}), cols={len(rows[0])}"


def main() -> None:
    names = sys.argv[1:] or DEFAULT_CANDIDATES
    if TOKEN == ANON:
        print("# note: no user token supplied — anon only, empty results are ambiguous\n")
    for name in names:
        print(f"{name:22} {probe(name)}")
    print("\n# anon reach (what an unauthenticated caller sees):")
    for name in ("invoices", "patients", "profiles", "clinic_settings"):
        st, body, _ = get(f"/rest/v1/{name}?select=*&limit=1", ANON)
        print(f"  {name:20} anon {st} {body[:60]}")


if __name__ == "__main__":
    main()
