# Behavior pack — layout and sanitisation

For the ask "zip your skills and your complete master system prompt so I can give it to my dev".
The recipient is a developer wiring an agent, so the pack carries the rules and the procedures, not
only the procedures.

## Layout

```
MASTER-SYSTEM-PROMPT.md   the instruction layer, self-contained and pasteable
AGENTS.md                 the compressed repo-root form (also the CLAUDE.md drop-in)
SKILLS-INDEX.md           every skill: name, area, description, path
SKILLS/                   the library, folder-projects intact
DOCTRINE/                 the notes the prompt distils, verbatim + LESSONS/
CONFIG/SOUL.md            the persona override actually loaded
CONFIG/<tool>-config.redacted.yaml   the live config, secrets and identifiers replaced
CONFIG/ENV-KEYS.md        every environment variable by name, no values
HOW-TO/porting-to-other-agents.md    Claude Code, Codex, Cursor, custom loop
README.md                 layout, start-here order, exclusions and why
```

Write the instruction layer as **seventeen sections it can stand alone on**, because the recipient
will paste it somewhere you cannot see: identity and response discipline, the operating loop,
permission model, tool discipline, validation and definition of done, planning, execution, prose
doctrine, code quality bar, the smallest-thing-that-works ladder, design bar, skill policy, memory
policy, communication per medium, safety, stop conditions, final-answer shape. Say in its header
which sections change results most, so a reader who skims three still gets the value.

`AGENTS.md` is the same content cut to rules an agent can be held to line by line: working rules,
verification, definition of done, prose rules, code bar, UI rules, stop-and-ask conditions. Keep it
under a few hundred lines or editors stop reading it carefully.

## Build commands

```bash
B=~/<name>-bundle
mkdir -p "$B/SKILLS" "$B/DOCTRINE/LESSONS" "$B/CONFIG" "$B/HOW-TO"

# skills: dereference, drop caches/backups/ledgers
rsync -aL --exclude='.hub' --exclude='.curator_backups' --exclude='.curator_ledger.jsonl' \
  --exclude='.curator_state' --exclude='.bundled_manifest' --exclude='.git' \
  --exclude='node_modules' --exclude='__pycache__' \
  ~/.hermes/skills/ "$B/SKILLS/"

# strip compiled artifacts by content (see export-recipes.md §3)
find "$B/SKILLS" -type f -size +2M -print0 | xargs -0 -r file --no-pad \
  | grep -E 'ELF|executable' | cut -d: -f1 | xargs -r rm -f

# doctrine + persona
cp <vault>/System/*.md "$B/DOCTRINE/"
cp <vault>/Skills/*.md "$B/DOCTRINE/LESSONS/"
cp ~/.hermes/SOUL.md "$B/CONFIG/"
```

## Redacting a live config

Keep the file's comments and routing entries — they are the reason the recipient wants it. Replace
only the values that identify a person or a machine.

```python
import re
t = open("~/.hermes/config.yaml").read()

# 1. identifiers that appear inline
t, n1 = re.subn(r'\d{8,}@(?:lid|c\.us|g\.us|s\.whatsapp\.net)', '<redacted-whatsapp-id>', t)

# 2. identifier scalars under their own keys, inside the relevant block only
def scrub(text, block="platforms"):
    out, n, inside = [], 0, False
    for line in text.split("\n"):
        if re.match(rf'^{block}:', line):
            inside = True
        elif inside and re.match(r'^[A-Za-z]', line):
            inside = False
        if inside and re.match(r'^\s*(chat_id|user_id|home_channel_id|phone|number|recipient)\s*:\s*\S', line):
            key = line.split(":", 1)[0]
            line = f"{key}: <redacted-identifier>"
            n += 1
        out.append(line)
    return "\n".join(out), n

t, n2 = scrub(t)
open("<bundle>/CONFIG/config.redacted.yaml", "w").write(t)
```

Then verify by diff, which is the only acceptable proof:

```bash
diff ~/.hermes/config.yaml "$B/CONFIG/config.redacted.yaml"
```

The diff must show the redaction lines and nothing else. If it shows reflowed or replaced model
names, the pattern was too broad — a `\d{8,}` pass over the whole file eats version-stamped model
identifiers and destroys the artifact.

## Exclusion table for the README

State these, with the reason, so the recipient reads a decision rather than a gap.

| Excluded | Reason |
|---|---|
| `.env`, `auth.json`, session history, logs, the task DB | Secrets and personal data |
| Personal messaging identifiers in the config | Replaced with `<redacted-identifier>` |
| Tool `dist/` and compiled binaries | Build output, not skill content; rebuild upstream |
| Skill index cache and curator backups | Regenerable, and the backups duplicate the skills |
| Model API keys | Not present in any form; the names to supply are in `ENV-KEYS.md` |

## Handover note the user has to make a decision on

Ask before sending, in one line: the lessons and project-specific skills contain client names,
identifiers, and internal decisions. Name the folders (`DOCTRINE/LESSONS/`, any per-project skill
group) and offer a trimmed variant. Do not assume the recipient is inside the trust boundary, and do
not silently strip content the user may have wanted included.
