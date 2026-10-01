# Agent context files — where instructions load from, and their precedence

## What an agent host injects automatically

Hermes injects two independent layers into every session's prompt:

1. **`SOUL.md` from the Hermes home directory** (`~/.hermes/SOUL.md` by default) — the identity slot, loaded regardless of working directory, capped by a budget. Put standing, cross-project rules here and nothing else.
2. **Exactly ONE project context type, first found wins**, in this order:
   - `.hermes.md` / `HERMES.md` — nearest match walking up to the git root
   - `AGENTS.md` chain — every directory from the git root down to the working directory, merged; per directory `AGENTS.override.md` beats `AGENTS.md` beats `agents.md`, and identical content down the chain is de-duplicated
   - `CLAUDE.md` / `claude.md` — working directory only
   - `.cursorrules` plus `.cursor/rules/*.mdc` — working directory only

## Consequences worth designing around

- **One type only.** A `.hermes.md` anywhere up the tree shadows the whole `AGENTS.md` chain for Hermes, even though other CLIs still read `AGENTS.md`. Do not ship both expecting both to load. Default to `AGENTS.md` for portability across CLIs and Codex-style agents; use `.hermes.md` only when the rules are Hermes-specific.
- **A git root above the project widens the blast radius.** If a parent directory is the repo root and carries an `AGENTS.md`, it applies to every project under it. Put project rules in the project's own directory so only that project picks them up.
- **Empty directories are invisible.** A folder with no files cannot be tracked, and a context file placed in a directory the session is not rooted in does nothing.

## Agent-instruction files are protected names

Writes to `AGENTS.md` and similar instruction files can be gated behind an approval prompt. If a write comes back blocked for that reason:

- **Do not retry the same content under a different filename or through another tool.** Same content under another name is the same edit.
- Stop, state the file and what it will contain in one line, and ask the user to approve — offering them the alternative of a non-protected filename (for example `agents/05-standing-rules.md`) and a "skip for now" option.
- A timeout on the prompt is not consent. Report it as blocked and continue with everything else that is not gated.

## Wiring an external doctrine vault into every session

When the user keeps a knowledge vault (an Obsidian vault, a notes repo) and calls it the agent's brain or context:

1. Read the vault's own index first and follow it to the doctrine notes; do not summarise from filenames.
2. Point the environment at it durably — an `OBSIDIAN_VAULT_PATH`-style variable in the host's env file (back the file up before appending), so path-resolving skills stop hunting.
3. Add a **compact pointer block** to `SOUL.md`: the vault path, and one line per note saying what to read it for. Pointers, not copies — the notes stay the source of truth and get re-read on demand.
4. Keep a pointer in the project's `AGENTS.md` too, naming the vault's quality notes and stating that the project's own `AGENTS.md` wins on conflict.
5. If persistent memory is the destination instead, store the pointer (path plus what lives where), never a copy of the doctrine; a full doctrine in always-injected context is expensive and goes stale.
