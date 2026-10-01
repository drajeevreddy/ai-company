#!/usr/bin/env python3
"""Snapshot and diff outbound refs across a static multi-page site.

Proves a bulk edit (re-theme, nav restyle, tag injection) changed no links:
snapshot BEFORE, edit, then diff AFTER. Added refs are allowed; any ref
present before but missing after fails the check (exit 1).

Usage:
  python3 href_snapshot.py snapshot <site_root> -o /tmp/refs_before.json
  # ... make edits ...
  python3 href_snapshot.py diff /tmp/refs_before.json <site_root>

Covers *.html at any depth. Reads tolerant of CRLF/odd encodings.
"""
import json
import re
import sys
from pathlib import Path

REF_RE = re.compile(r'''(?:href|src)\s*=\s*["']([^"'#]+?)["']''')


def snapshot(root: str) -> dict:
    out = {}
    for f in sorted(Path(root).rglob("*.html")):
        try:
            html = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        out[str(f.relative_to(root))] = REF_RE.findall(html)
    return out


def cmd_snapshot(root: str, dest: str) -> None:
    data = snapshot(root)
    Path(dest).write_text(json.dumps(data, indent=1), encoding="utf-8")
    total = sum(len(v) for v in data.values())
    print(f"pages: {len(data)}, total refs: {total} -> {dest}")


def cmd_diff(before_path: str, root: str) -> int:
    before = json.loads(Path(before_path).read_text(encoding="utf-8"))
    after = snapshot(root)
    ok = True
    for page in sorted(set(before) | set(after)):
        old, new = before.get(page, []), after.get(page, [])
        if page not in after:
            ok = False
            print(f"PAGE REMOVED: {page}")
            continue
        missing = [h for h in old if h not in new]
        if missing:
            ok = False
            print(f"MISSING in {page}: {missing}")
    print("ALL ORIGINAL REFS INTACT" if ok else "REF CHECK FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] not in ("snapshot", "diff"):
        sys.exit("usage: href_snapshot.py snapshot <root> -o <out> | diff <before.json> <root>")
    if sys.argv[1] == "snapshot":
        if "-o" not in sys.argv:
            sys.exit("snapshot needs -o <out.json>")
        cmd_snapshot(sys.argv[2], sys.argv[sys.argv.index("-o") + 1])
    else:
        sys.exit(cmd_diff(sys.argv[2], sys.argv[3]))
