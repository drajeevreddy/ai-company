---
name: hermes-persistent-context
description: "Wire vaults and project rules into Hermes context."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [hermes, context, soul-md, agents-md, vault, memory, configuration]
    related_skills: [hermes-agent, obsidian]
    requires_tools: [terminal, read_file, write_file, patch, search_files]
---

# Hermes Persistent Context

Use when knowledge, doctrine, a vault, or project rules must persist into future Hermes sessions — the user says "this is your brain", "always follow these rules", "remember this for the project". The job: pick the layer, write the pointer, verify it injects, report what was wired.

## Pick the layer first

| Content | Layer | When it loads |
|---|---|---|
| Identity, voice, standing rules for every session | `$HERMES_HOME/SOUL.md` | Every prompt, any cwd |
| Rules for one repo / project tree | `.hermes.md` / `AGENTS.md` / `CLAUDE.md` / `.cursorrules` | Every prompt in that cwd — **only one of these loads** |
| Procedure for a class of task | a skill (`skill_manage`) | When the task matches |
| Short durable fact: who the user is, environment, standing convention | memory | Every turn, char-budgeted |
| The actual content: vault notes, specs, code, docs | stays where it is | On demand, via a read |

Everything above except the last row is a **pointer**, never a copy. Writing doctrine into SOUL.md or memory duplicates the source, drifts from it, and is paid for on every turn of every session.

## Procedure

1. **Resolve the home.** `hermes config path`, `hermes config env-path`, and honor `$HERMES_HOME` when set (profiles use `~/.hermes/profiles/<name>/`). Never hardcode `~/.hermes` when a profile may be active.
2. **Read the target file whole before writing it.** `write_file` replaces the entire file; SOUL.md holds the identity paragraph and must survive byte-for-byte. Re-read it in the same session you edit it.
3. **Write a compact pointer block.** Path, one line per note saying what it is for, and the instruction to read it rather than trust the summary. A few lines. Include *when* to read each thing, not the content itself.
4. **Register external paths as env vars** when a skill resolves them (e.g. `OBSIDIAN_VAULT_PATH` for the `obsidian` skill): back up the env file (`cp .env .env.bak.<reason>`), append the key with a comment, then grep the added line back. `hermes config set` writes config.yaml and **cannot** set an env var — env keys go in the file `hermes config env-path` prints.
5. **Add the matching memory pointer** when the fact applies to every session regardless of task. Point at the path; do not restate the content. Declarative phrasing, not an instruction to yourself.
6. **Verify.** Grep the file for the lines you added, confirm the byte count changed, confirm the env line landed. Do not report persistence off a successful write call alone.

## Pitfalls

- **Only one project context type loads, first found wins:** `.hermes.md`/`HERMES.md` (walking up to the git root) → `AGENTS.md` chain (git root → cwd) → `CLAUDE.md` (cwd) → `.cursorrules` + `.cursor/rules/*.mdc` (cwd). Adding `AGENTS.md` while a `.hermes.md` exists at or above the cwd does nothing — check for a higher-priority file before writing one.
- **`.hermes.md` is discovered by walking up to the git root**, so in a monorepo-style tree a file in a subfolder can be shadowed by one higher up. Confirm discovery with the file actually in place.
- **Never put secrets in any context file.** SOUL.md, AGENTS.md, `.hermes.md`, `.cursorrules` are injected into every prompt of every session.
- **SOUL.md has a per-turn cost.** A pointer block of a few lines is right; pasting the doctrine in is not. Depth belongs in the source file, read on demand.
- **Never print the env file.** Show key names with `grep -o '^[A-Z_]*=' <env-file>` and grep for the single key you added; print no values.
- **Re-read the source of truth when the answer depends on it.** Do not answer "how does Hermes load X" from a summary in this skill — read the module (see `references/hermes-source-map.md`).
- **Do not duplicate always-loaded context inside a skill.** If the rule already lives in SOUL.md or an AGENTS.md, a skill restating it double-loads and rots at a different rate.

## Pattern: doctrine vault as the agent's brain

A markdown/Obsidian vault holding the agent's operating doctrine, capability map, and per-project facts is wired in three moves: a SOUL.md pointer block naming the vault and which note to read for each kind of work; the vault path set as an env var if a vault skill resolves it; and a one-line memory pointer so a session knows the vault exists before it knows what is in it. The notes stay the source of truth — the wiring only guarantees they get found.

## Reference

- `references/hermes-source-map.md` — where things live in a git-installed Hermes tree, for verifying context-injection behaviour in source rather than from memory.
