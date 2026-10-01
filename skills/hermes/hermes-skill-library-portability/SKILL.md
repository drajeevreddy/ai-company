---
name: hermes-skill-library-portability
description: Export a Hermes skill library to another machine.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [skills, export, migration, backup, packaging, hermes-home]
    category: autonomous-ai-agents
    related_skills: [hermes-agent, hermes-skill-discovery-install, hermes-agent-skill-authoring]
---

# Hermes Skill Library Portability

## Overview

Move a working skill library to another machine, another profile, or into a handoff pack: export
it whole, ship it so the recipient runs one command, snapshot it before a bulk edit, or hand a
developer the agent's whole behaviour layer. Two pack shapes: a **skills archive** (skills only)
and a **behavior pack** (skills plus the instruction layer, the persona, and a scrubbed config).
This skill covers what to dereference, what to exclude, how to redact, and how to prove the pack is
both complete and clean before sending it. It is the export/import direction; discovering and
batch-installing skills from GitHub is `hermes-skill-discovery-install`, and authoring the
instruction layer itself is `agent-build-packs`.

## When to Use

- "Export all my skills", "make my friend's Hermes like mine", "clone my setup for X"
- "Zip your skills and your system prompt so I can give it to my dev" — a behavior pack, see below
- Snapshotting `~/.hermes/skills` before a bulk edit, migration, or Hermes upgrade
- Moving skills into another profile (`~/.hermes/profiles/<name>/skills`)

## Establish the Library First

1. Root is `~/.hermes/skills`; profile root is `~/.hermes/profiles/<name>/skills`.
2. The layout is mixed, and this is the part that breaks naive archiving: category dirs
   (`autonomous-ai-agents/<skill>/SKILL.md`), standalone skill dirs, **and symlinked skill dirs**
   pointing at project repos or other agent trees (`~/.claude/skills`, `~/.agents/skills`). `find`
   does not descend into symlinks — enumerate them explicitly with
   `find <root> -maxdepth 1 -type l -printf "%f -> %l\n"`.
3. The authoritative loaded set is `~/.hermes/.skills_prompt_snapshot.json`: `skills` (list),
   `manifest` (dict), `category_descriptions`. Verify the archive against the length of `skills`,
   not against a directory listing — that is the set Hermes actually shows the model.

## Procedure

1. **Inventory and count** the source: real `SKILL.md` files without symlink descent, then with
   (`find -L`). The gap between the two numbers is the symlinked set that must be dereferenced.
2. **Read the symlink map** so you know which skills go dangling under a naive tar, and which
   point at personal project repos the recipient may not have.
3. **Scan for secrets before packaging.** Skills legitimately quote example credentials; read every
   hit instead of trusting the pattern:

   ```bash
   cd ~/.hermes/skills
   grep -rIlE "(sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{30,}|xox[baprs]-|-----BEGIN [A-Z ]*PRIVATE KEY-----)" .
   ```

   Placeholders such as `ghp_xx...xxxx` in MCP/CLI example docs are normal. A real token means
   stop, report it, and exclude or rotate before shipping.
4. **Triage the dereferenced tree, then build the archive** (run from the library root):

   ```bash
   cd ~/.hermes/skills
   find -L . -path './.hub' -prune -o -path './.curator_backups' -prune \
     -o -name node_modules -prune -o -name .git -prune \
     -o -type f -size -1000k -print0 | tar czhf <out>/hermes-skills.tar.gz --null -T -
   ```

   `find -L` plus `--null -T -` is what carries symlinked skills in as real file content; the size
   filter drops compiled binaries. Triage **before** archiving and triage the **dereferenced** tree:
   the binaries live behind the symlinks, so `du` on the source root under-reports by 5x or more and
   the exclusions look unnecessary until the pack lands. Strip executables by content, not by
   directory name — `find -L . -type f -size +2M -print0 | xargs -0 file --no-pad | grep -E 'ELF|executable'`
   then delete the cut paths. A tool's `dist/` and `bin/` are the common locations but not the only
   ones, and a name-pattern exclusion silently misses the rest.
5. **Verify the archive before shipping** — extract to a scratch dir, count `SKILL.md`, and check
   every one opens with `---`. A near-empty tarball is the signature of an empty file list
   (Pitfall 1).
6. **Package the handoff**: the archive plus `MANIFEST.md` (every skill with path + description),
   `INSTALL.md` (what is in, what is deliberately out, dependency notes), and an `install.sh`, all
   bundled into one transferable `.tar.gz` so the recipient receives a single file.
7. **Test `install.sh` against a throwaway HOME before handing it over** — `HOME=/tmp/htest bash
   install.sh` with a dummy pre-existing skills dir proves the backup step, the extract, and the
   count check without touching the real profile.

## Handoff Contract

A pack is complete when the recipient does this and nothing else:

```bash
tar xzf hermes-skills-export.tar.gz && cd hermes-skills-export && ./install.sh
```

`install.sh` must be non-destructive by default: move any existing `skills/` aside to
`skills.bak.<timestamp>`, extract, then count `SKILL.md` and fail loudly if short. Support a
profile argument and a `--merge` mode that only adds missing skills. Template:
`templates/install-skills-pack.sh`.

## Behavior Packs (skills + instruction layer)

When the ask is "my skills and your system prompt" rather than "my skills", the recipient needs the
rules, not only the procedures. Ship this layout; the individual files stay authoritative and a
single concatenated copy is added for one-pass reading:

```
MASTER-SYSTEM-PROMPT.md   the instruction layer, self-contained: identity, operating loop,
                          permission model, tool discipline, validation and definition of done,
                          planning, execution, prose doctrine, code bar, laziness ladder, design
                          bar, skill policy, memory policy, communication, safety, stop conditions
AGENTS.md                 the same rules compressed for a repo root (also the CLAUDE.md drop-in)
SKILLS-INDEX.md           every skill: name, area, description, path
SKILLS/                   the library
DOCTRINE/                 the source notes the prompt distils, verbatim, plus LESSONS/
CONFIG/                   SOUL.md (persona) · redacted config · ENV-KEYS.md (names, no values)
HOW-TO/                   porting to Claude Code, Codex, Cursor, or a custom loop
README.md                 layout, start-here order, what was excluded and why
```

Assembly notes that decide whether it is usable:

- **A skill is a folder, so publish the folder.** `SKILLS/` keeps each skill's `references/`,
  `templates/`, and `scripts/` intact; flattening to `SKILL.md` files loses the support material the
  skills actually invoke.
- **Generate `SKILLS-INDEX.md` by parsing frontmatter**, not by grepping `description:`. Load the
  YAML block with a real parser and fall back to reading the first heading when it fails; see
  `references/export-recipes.md` §6 for the block-scalar trap.
- **`ENV-KEYS.md` lists variable names and no values.** A named key the recipient must supply is the
  whole point; a value is the leak.
- **State the exclusions and the reason in the README**, so the recipient knows the compilers are
  absent on purpose rather than broken.
- **Say what in the pack is not the recipient's to read.** Lessons and project-specific skills carry
  client names, identifiers, and internal decisions. Name the folders to skim before sending and
  offer a trimmed variant; do not assume a recipient is inside the trust boundary.

## What Never Rides Along

Skills are portable know-how; these are this machine's state and stay behind unless the user
explicitly asks for a full clone:

- `~/.hermes/MEMORY.md`, `~/.hermes/memories/USER.md` — personal facts about the owner
- `~/.hermes/config.yaml` — models, providers, machine settings
- `~/.hermes/.env` — API keys and secrets
- `~/.hermes/cron/`, `state.db`, `sessions/` — job and conversation history

When the user wants the recipient wired the same way, build a **scrubbed** config separately
(settings with keys stripped) rather than bundling the live one. State plainly which of the above
was left out and why — the user is deciding what to share, so surface the choice instead of
silently making it.

## Pitfalls

1. **`find -size -1M` matches only empty files.** GNU `find` rounds a file's size UP to the unit,
   so any non-empty file is already `1M` and fails `<1M`; the file list comes out empty and tar
   writes a ~130-byte archive. Use `-size -1000k`, and treat a suspiciously small archive as this
   bug rather than as "the library is small".
2. **A plain `tar czf` on the library root silently ships dangling symlinks.** Every symlinked skill
   arrives as a dead pointer — it still loads for the recipient but has no content. Always `-L`/`-h`,
   and count `SKILL.md` after extraction to prove it.
3. **Decide exclusions from measurements, not guesses** — ignoring blob sizes produces a pack nobody
   can send. Compiled helper binaries, `.hub` index caches, and curator backups inflate the tree by
   10-20x. Measure with `du -shL --exclude=.hub --exclude=.curator_backups */ | sort -rh | head -20`
   and `find -L . -type f -size +1M -printf "%s\t%p\n" | sort -rn | head -25`. A pack of a few
   hundred prose skills is single-digit MB; an archive over ~50MB is carrying binaries or caches.
4. **Platform-specific build artifacts are not skills.** Executables inside a skill's `dist/` are
   arch-bound and rebuildable by re-installing the upstream tool — exclude them and tell the
   recipient to get them from upstream.
5. **A manifest built with a naive `description:` regex shows `>-` for multi-line frontmatter.**
   YAML block scalars (`>-`, `>`, `|`) must be detected and their indented continuation lines
   joined, or that slice of the manifest is unusable. Recipe: `references/export-recipes.md`.
6. **Do not report "no secrets" from a clean grep alone.** Read the matched file — example
   credentials in prose are the common false positive, and a false alarm trains the user to ignore
   the scan. Report the file, the line, and why it is a placeholder.
7. **A secret scan over the source does not prove the pack is clean.** It matches key *shapes*. Two
   other classes ride along and neither trips it: personal identifiers (phone numbers, WhatsApp
   `@lid` / `@c.us` JIDs, chat and home-channel ids, emails) and machine paths. Prove the finished
   pack by *value*: build a pattern file of every value from the source `.env` and config, then
   `grep -rFl -f values.txt <bundle>` and read every hit. A hit on a path or a display name is a
   false positive; a hit on an identifier is a finding. Script: `scripts/verify-no-value-leaks.sh`.
8. **Redact identifiers by key path, never with a blanket numeric regex.** A `\d{8,}` substitution
   applied to a whole config file eats version-stamped model names
   (`claude-haiku-4-5-20251001`, `o3-2025-04-16`), producing a config that is worse than useless to
   the recipient. Redact scalars under the specific keys (`chat_id`, `user_id`, `phone`,
   `home_channel`, `recipient`) inside the relevant block, then run `diff` against the original: if
   the diff shows anything beyond the redaction lines, the pattern was too broad.
9. **Do not silently exclude the config when the ask was for a working reference.** The default is
   exclude; when the user wants it, ship the redacted copy, keep every comment and routing entry
   intact, and say in the README exactly which lines were replaced. Two redacted lines in a
   1,000-line config is a better artifact than a missing file.

## Verification Checklist

- [ ] Symlink map read; symlinked skills confirmed in the archive as real files
- [ ] `SKILL.md` count in the archive matches the `skills` list in `.skills_prompt_snapshot.json`
- [ ] Every extracted `SKILL.md` starts with `---` frontmatter
- [ ] Secret scan run and every hit read, not just counted
- [ ] Value-level leak check run against the finished pack; every hit triaged as finding or false positive
- [ ] Config redaction verified by `diff`: only the redaction lines differ from the source
- [ ] Behavior pack (if shipped) carries the instruction layer, a persona file, env key names, and a
      porting note; a single concatenated read-through copy exists
- [ ] Caches, curator backups, and `>1M` binaries excluded; compressed size in the expected range
- [ ] `install.sh` exercised under a throwaway `HOME` (backup + extract + count all verified)
- [ ] Personal state (memory, config, `.env`, cron, sessions) excluded, and the user told

## References

- `references/export-recipes.md` — enumeration, size triage, archive/verify one-liners, manifest builder
- `references/behavior-pack-contents.md` — the behavior-pack layout, config redaction recipes, and the exclusion table for the README
- `scripts/verify-no-value-leaks.sh` — prove no source value appears anywhere in a finished pack
- `templates/install-skills-pack.sh` — non-destructive installer to copy and adjust
