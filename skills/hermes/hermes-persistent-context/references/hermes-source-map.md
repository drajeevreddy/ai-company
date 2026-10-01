# Hermes source map (git-installed tree)

Where to look when a question is about *how Hermes behaves* and a summary is not enough. Verify with `search_files` first — paths move between versions.

## Locating the tree

- `which hermes` is a bash wrapper (e.g. `~/.local/bin/hermes`) that execs `<HERMES_HOME>/hermes-agent/venv/bin/python <HERMES_HOME>/hermes-agent/hermes "$@"` after unsetting `PYTHONPATH`/`PYTHONHOME`. Read it to find the real tree — Hermes is not a pip-installed module in that layout.
- Source: `$HERMES_HOME/hermes-agent/`. CLI entry points: `hermes_cli/main.py`; command help: `hermes <command> --help`.

## Context injection (the part this skill is about)

- `agent/prompt_builder.py`
  - `build_context_files_prompt()` — the router. Loads exactly one project context file, first non-empty of `_load_hermes_md` → `_load_agents_md` → `_load_claude_md` → `_load_cursorrules`; SOUL.md is appended independently unless `skip_soul`.
  - `load_soul_md()` — reads `$HERMES_HOME/SOUL.md`, threat-scans it, caps it to the context budget.
  - `_load_hermes_md()` / `_load_agents_md()` / `_load_claude_md()` / `_load_cursorrules()` — the individual loaders, each with its own search rule.
  - `_agents_md_directory_chain()` — AGENTS.md chain from git root down to cwd; per directory the first of `AGENTS.override.md` / `AGENTS.md` / `agents.md` wins, identical content further down the chain is skipped.
  - `_find_git_root()` / `_find_hermes_md()` — how far up a search walks.
  - `_scan_context_content()` — context files are injection-scanned; matches block the file.
  - `_truncate_content()` — per-file character caps; oversized context files get truncated, not error.
- `agent/coding_context.py` — the repo map injected for coding work; recognises `AGENTS.md` / `CLAUDE.md` / `.cursorrules` as project markers.

## Config and state

- `~/.hermes/config.yaml` — settings (never secrets). `hermes config set/get/unset/path` operate here; `hermes config env-path` prints the `.env` path.
- `~/.hermes/.env` — credentials and env vars only. No CLI subcommand writes it; append by hand (back it up first, never print it).
- `$HERMES_HOME/skills/` — installed skills, grouped by category directory. Profile-scoped skills live under `~/.hermes/profiles/<name>/skills/`.
- `~/.hermes/state.db` — session store (SQLite + FTS5); `~/.hermes/sessions/` holds gateway routing and transcripts.

## Reading source without drowning

`search_files` with `output_mode='files_only'` over the tree for a function or string, then `read_file` with `offset`/`limit` around the match. Grep by *behaviour* ("context", "inject", "precedence") rather than by feature name — the name in the UI rarely matches the function name.
