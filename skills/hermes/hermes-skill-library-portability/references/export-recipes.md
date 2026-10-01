# Export recipes — Hermes skill library

Command set for packaging `~/.hermes/skills` (or a profile's skills dir). Run from the library
root unless noted.

## 1. Inventory

```bash
# skills as Hermes loads them (follows symlinks, skips caches)
find -L ~/.hermes/skills -name SKILL.md -not -path "*/.hub/*" -not -path "*/.curator_backups/*" | wc -l

# real files only — the difference is the symlinked set
find ~/.hermes/skills -name SKILL.md | wc -l

# the authoritative loaded count
python3 -c "import json,os;d=json.load(open(os.path.expanduser('~/.hermes/.skills_prompt_snapshot.json')));print(len(d['skills']), len(d['manifest']))"
```

`manifest` is usually slightly larger than `skills`; `skills` is the set to match.

## 2. Symlink map

```bash
cd ~/.hermes/skills
find . -maxdepth 1 -type l -printf "%f -> %l\n" | sort
find . -maxdepth 1 -type l | wc -l
find -xdev . -xtype l          # broken links, if any
```

Skill dirs commonly symlink to personal project repos (`~/<project>/skills/<skill>`) and to other
agent trees (`~/.claude/skills`, `~/.agents/skills`). Those skills still load for the recipient,
but scripts that reference the repo paths only run where the repo exists — say so in the handoff
notes.

## 3. Size triage — decide exclusions from measurements

```bash
# per-top-level-dir size, dereferenced
cd ~/.hermes/skills && du -shL --exclude=.hub --exclude=.curator_backups */ | sort -rh | head -20

# the few big blobs that explain the total
find -L . -path ./.hub -prune -o -path ./.curator_backups -prune -o \
  -type f -size +1M -printf "%s\t%p\n" | sort -rn | head -25

# supporting-file density — sanity that content is real, not SKILL.md stubs
find -L ~/.hermes/skills -type d \( -name scripts -o -name references -o -name templates \) | wc -l
find -L ~/.hermes/skills -type f | wc -l
```

Large hits fall into three buckets, all excluded by default:

| Bucket | Example | Why it goes |
|---|---|---|
| Compiled helper binaries | a skill's `dist/` executables | arch-bound, recipient reinstalls upstream |
| Catalog cache | `.hub/index-cache/` | regenerated on demand, tens of MB |
| Library snapshots | `.curator_backups/<ts>/skills.tar.gz` | the pack inside the pack |

### Triage the dereferenced tree, not the source root

`du -sh ~/.hermes/skills` does not follow symlinks, so it counts none of the content that will
actually ship. Dereferencing is what grows the pack, and the growth is almost always binaries inside
symlinked project repos — a library measured at 77 MB landed at 385 MB after `rsync -aL`, because one
symlinked tool repo carried four 94 MB compiled executables that no name-pattern exclusion
(`dist/`, `bin/`) would have been enough to find reliably.

```bash
# measure the dereferenced tree, per top-level area
rsync -aL --dry-run --stats ~/.hermes/skills/ /tmp/measure/ 2>/dev/null | tail -5
du -shL --exclude=.hub --exclude=.curator_backups ~/.hermes/skills/* | sort -rh | head -20

# strip executables by CONTENT, then confirm nothing large is left
find -L <copy> -type f -size +2M -print0 | xargs -0 -r file --no-pad \
  | grep -E 'ELF|executable' | cut -d: -f1 | tee /tmp/bin.list
xargs -r rm -f < /tmp/bin.list
find <copy> -type f -size +5M -printf '%s\t%p\n' | sort -rn | head
```

A few hundred prose skills plus their references is tens of MB. If the zipped pack is hundreds of MB,
run the content check above before concluding the library is simply large.

## 4. Build the archive

```bash
mkdir -p ~/hermes-skills-export && cd ~/.hermes/skills
find -L . -path './.hub' -prune -o -path './.curator_backups' -prune \
  -o -name node_modules -prune -o -name .git -prune \
  -o -type f -size -1000k -print0 | tar czhf ~/hermes-skills-export/hermes-skills.tar.gz --null -T -
```

Notes that cost time when missed:

- `-size -1000k`, never `-size -1M` — GNU `find` rounds a file's size up to the unit, so `-1M`
  matches only zero-byte files and the archive comes out ~130 bytes.
- `find -L` turns symlinked skills into real content; `tar -h` covers any symlink form `find` did
  not already resolve.
- Filtering on `-size` instead of tool-name patterns keeps working when a skill reorganises.
- Files only (no directory entries) is fine — tar creates parents on extract.

## 5. Verify

```bash
ls -lh ~/hermes-skills-export/
tar tzf ~/hermes-skills-export/hermes-skills.tar.gz | wc -l
tar tzf ~/hermes-skills-export/hermes-skills.tar.gz | grep -c 'SKILL.md$'

rm -rf /tmp/skillverify && mkdir -p /tmp/skillverify
tar xzf ~/hermes-skills-export/hermes-skills.tar.gz -C /tmp/skillverify
find /tmp/skillverify -name SKILL.md | wc -l

# every skill must open with frontmatter
for f in $(find /tmp/skillverify -name SKILL.md); do head -1 "$f" | grep -q '^---' || echo "NO-FM: $f"; done
```

The `SKILL.md` count must equal the `skills` list length from `.skills_prompt_snapshot.json`.

## 6. Manifest builder (frontmatter-aware)

A regex on `description:` alone yields `>-` for skills whose description is a YAML block scalar.
Detect the scalar and join its indented continuation lines:

```python
import os, re

BLOCK = (">-", ">", "|", "|-", "")

def parse_desc(fm):
    lines = fm.split("\n")
    for i, line in enumerate(lines):
        m = re.match(r'^description:\s*(.*)$', line)
        if not m:
            continue
        value = m.group(1).strip()
        if value in BLOCK:
            buf = []
            for nxt in lines[i + 1:]:
                if re.match(r'^\s+\S', nxt):
                    buf.append(nxt.strip())
                elif nxt.strip() == "":
                    continue
                else:
                    break
            return " ".join(buf).strip()
        return value.strip('"\'')
    return ""

def rows(root):
    out = []
    for dirpath, _dirs, files in os.walk(root):
        if "SKILL.md" not in files:
            continue
        txt = open(os.path.join(dirpath, "SKILL.md"), encoding="utf-8", errors="replace").read()
        m = re.search(r'^---\s*\n(.*?)\n---', txt, re.S)
        fm = m.group(1) if m else ""
        nm = re.search(r'^name:\s*(.+)$', fm, re.M)
        nm = nm.group(1).strip().strip('"\'') if nm else os.path.basename(dirpath)
        out.append((nm, os.path.relpath(dirpath, root), parse_desc(fm)))
    return out
```

Rows with an empty or sub-8-char description mean the frontmatter split failed on that file — fix
the parse before shipping the manifest. Group rows by first path segment, sort large groups first,
and the group sizes double as the "contents by area" summary at the top of the manifest.

## 7. Bundle and checksum

```bash
cd ~/hermes-skills-export
tar czf hermes-skills-export.tar.gz hermes-skills.tar.gz install.sh INSTALL.md MANIFEST.md
gzip -t hermes-skills-export.tar.gz && echo "gzip OK"
sha256sum hermes-skills.tar.gz hermes-skills-export.tar.gz
```

Give the recipient the sha256 so a truncated transfer is visible before they extract.

## 8. Prove no value leaked (run this on the finished pack)

A key-shape grep over the source cannot see personal identifiers or machine paths. Check the pack by
**value** instead:

```bash
grep -oE '^[A-Za-z_][A-Za-z0-9_]*=.*' ~/.hermes/.env | sed 's/^[^=]*=//' | tr -d '"' | tr -d "'" \
  | awk 'length($0)>=16' | grep -vE '^https?://' | sort -u > /tmp/secretvals.txt

# every hit is a file in the pack that contains a value from the environment
grep -rlF -f /tmp/secretvals.txt <pack-dir>
```

Triage, do not count: a hit on a path (`/home/.../Some Vault`) or a display name is a false
positive and belongs in the README's exclusion note; a hit on a phone number, a WhatsApp `@lid`,
a chat id, an email, or a token-shaped string is a finding and blocks the handoff until redacted.
Re-run the same grep after redacting — the check is the acceptance test, not the redaction.

Companion script: `scripts/verify-no-value-leaks.sh` (takes the environment file and the pack path).
