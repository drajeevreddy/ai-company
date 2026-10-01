#!/usr/bin/env python3
"""Static-site link & asset integrity checker (server-aware).

Resolves refs the way Apache actually does: extensionless URLs try
.html/.php, directory URLs fall back to index.html/index.php, %20 is
URL-decoded, ?query/#hash stripped, and ../-relative links resolve from
each file's own directory (catches wrong-depth links).

Usage: python3 check_links.py [root_dir]
Exit 0 always; prints grouped findings (grouped = one systemic bug
shows as one issue, not thousands).
"""
import os
import re
import sys
import urllib.parse

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
os.chdir(ROOT)

all_files = set()
for dp, dn, fn in os.walk("."):
    if "/." in dp or dp.startswith("./."):
        continue
    for f in fn:
        all_files.add(os.path.join(dp, f)[2:].replace(os.sep, "/"))


def exists(resolved: str) -> bool:
    if resolved in all_files:
        return True
    if "." not in os.path.basename(resolved):  # extensionless clean URL
        for ext in (".html", ".php"):
            if resolved + ext in all_files:
                return True
    for idx in ("index.html", "index.php"):  # directory index
        if os.path.join(resolved, idx) in all_files:
            return True
    return False


def resolve(base_dir: str, ref: str):
    ref = urllib.parse.unquote(ref).split("?")[0].split("#")[0]
    if not ref or ref.startswith(
        ("/", "http:", "https:", "mailto:", "tel:", "javascript:", "data:", "//")
    ):
        return None  # absolute / external / scheme — not verifiable locally
    if ref == ".":
        return os.path.normpath(base_dir).replace(os.sep, "/") or "."
    return os.path.normpath(os.path.join(base_dir, ref)).replace(os.sep, "/")


issues = {}  # (resolved, ref) -> [files]
checked = 0
for dp, dn, fn in os.walk("."):
    if "/." in dp or dp.startswith("./."):
        continue
    for f in fn:
        if not f.endswith((".html", ".htm")):
            continue
        full = os.path.join(dp, f)
        base_dir = os.path.dirname(full)
        try:
            with open(full, encoding="utf-8", errors="replace") as fh:
                content = fh.read()
        except OSError:
            continue
        for m in re.finditer(r'(?:href|src)\s*=\s*["\']([^"\']+)["\']', content):
            ref = m.group(1).strip()
            if not ref:
                continue
            checked += 1
            res = resolve(base_dir, ref)
            if res is None:
                continue
            if not exists(res):
                issues.setdefault((res, ref), []).append(full)

print(f"Refs checked: {checked}; distinct broken targets: {len(issues)}")
for (res, ref), files in sorted(issues.items(), key=lambda kv: -len(kv[1])):
    print(f"{len(files)}x  {res}  (ref: {ref})  e.g. {files[0]}")
