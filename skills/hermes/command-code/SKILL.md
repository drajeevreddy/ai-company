---
name: command-code
description: "Delegate coding to Command Code CLI (features, fixes, PRs)."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Coding-Agent, Command-Code, Langbase, Autonomous, Refactoring]
    related_skills: [claude-code, codex, opencode, cursor-agent, vibe, mimo, hermes-agent]
---

# Command Code CLI (`cmd`)

Use [Command Code](https://commandcode.ai/docs) (by Langbase) as an autonomous coding worker orchestrated by Hermes terminal/process tools. Command Code is a coding agent that "continuously learns your taste of writing code" and is tuned for open models.

## When to Use

- User explicitly asks to use Command Code / `cmd`
- You want an external coding agent with taste-learning / personalization
- You want a coding agent that can import setup from other agents (Claude Code, Codex, Cursor, etc.)
- You need long-running sessions with progress checks or parallel worktrees

## Prerequisites

- Installed as npm global: `npm i -g command-code` → binaries `cmd`, `cmdc`, `command-code`, `commandcode` (all the same `dist/index.mjs`)
- Verify: `cmd --version` (also `cmd info`, `cmd status`)
- Auth: `cmd login` (Command Code account); `cmd status` shows auth state
- Git repository for code tasks (recommended)
- `pty=true` for interactive sessions

## Binary Resolution (Important)

The activation command is `cmd` — NOT `code` (VS Code). `cmdc` / `command-code` / `commandcode` are aliases of the same binary. If behavior differs between your terminal and Hermes:

```
terminal(command="which -a cmd cmdc command-code")
terminal(command="cmd --version")
```

## One-Shot Tasks (Print Mode)

Use `-p, --print` for bounded, non-interactive tasks:

```
terminal(command="cmd -p 'Add retry logic to API calls and update tests'", workdir="~/project")
```

Cap turns and get machine-readable output (NDJSON event stream + final result line):

```
terminal(command="cmd -p 'Implement OAuth refresh flow' --max-turns 30 --output-format json", workdir="~/project")
```

Skip the taste onboarding for automated runs:

```
terminal(command="cmd -p 'Refactor auth module' --skip-onboarding", workdir="~/project")
```

Planning mode and permission modes:

```
terminal(command="cmd -p 'Analyze the codebase and propose a plan' --plan", workdir="~/project")
terminal(command="cmd -p 'Fix the flaky test' --permission-mode auto-accept", workdir="~/project")
# --auto-accept and --yolo (alias for --dangerously-skip-permissions) also skip prompts
```

Force a specific model / reasoning effort:

```
terminal(command="cmd -p 'Add pagination to the API client' -m <model> --effort high", workdir="~/project")
# List models: cmd --list-models
```

Set any config headlessly:

```
terminal(command="cmd -p 'Update README' --config theme=dark", workdir="~/project")
```

## Interactive Sessions (Background)

For iterative work, start an interactive session in background:

```
terminal(command="cmd 'Implement OAuth refresh flow and add tests'", workdir="~/project", background=true, pty=true)
# Returns session_id

# Send follow-up input
process(action="submit", session_id="<id>", data="Now add error handling for token expiry")

# Monitor progress
process(action="poll", session_id="<id>")
process(action="log", session_id="<id>")

# Exit cleanly — Ctrl+C, or kill
process(action="write", session_id="<id>", data="\x03")
process(action="kill", session_id="<id>")
```

### Resuming / Forking Sessions

```
terminal(command="cmd -c", workdir="~/project", background=true, pty=true)                  # Continue last
terminal(command="cmd -r 'my session name'", workdir="~/project", background=true, pty=true) # Resume by id/name
terminal(command="cmd --session <path-or-id>", workdir="~/project", background=true, pty=true) # Resume by transcript path or session-id prefix
terminal(command="cmd -c --fork-session", workdir="~/project", background=true, pty=true)   # Fork (original untouched)
```

## Common Flags

| Flag | Use |
|------|-----|
| `-p, --print [query]` | Non-interactive mode: run, output, exit |
| `--max-turns N` | Cap turns in `-p` mode (default 100; exit code 8 on cap-hit) |
| `--output-format text\|json` | `-p` output: text or NDJSON events + final line |
| `-m, --model <model>` | Run on a specific model |
| `--effort <level>` | Reasoning effort (low/medium/high, per model) |
| `--plan` | Start in plan mode (read-only) |
| `--permission-mode standard\|plan\|auto-accept` | Permission mode |
| `--auto-accept` / `--yolo` | Skip permission prompts (`--yolo` = `--dangerously-skip-permissions`) |
| `-r, --resume [name]` | Resume by id/name or pick from history |
| `-c, --continue` | Continue last conversation |
| `--fork-session` | Fork on resume/continue |
| `--session <path\|id>` | Resume by transcript path or session-id prefix |
| `--no-session` | Don't persist session to disk |
| `-n, --name <name>` | Set session display name |
| `-t, --trust` | Auto-trust project |
| `--add-dir <directory>` | Add directory to workspace context |
| `-w, --worktree [name]` | Run in isolated managed worktree (name/path/#PR) |
| `--mod <path>` | Load a mod file/directory (repeatable) |
| `--skill <path>` | Load extra skills from a path (repeatable) |
| `--skip-onboarding` | Skip taste onboarding (for automated runs) |
| `--no-auto-update` | Disable background auto-update for this run |
| `--ide-setup` | Connect IDE to share open file / selected lines |

## Subcommands

| Command | Use |
|---------|-----|
| `cmd login` / `logout` | Auth with Command Code account |
| `cmd status` / `whoami` | Auth status / current user |
| `cmd info` | System information |
| `cmd update` | Update to latest |
| `cmd taste` | Manage taste learning packages |
| `cmd taste learn <source>` | Learn taste from a local repo or GitHub repo |
| `cmd learn-taste` | Learn command structure from repositories |
| `cmd mcp` | Manage MCP servers |
| `cmd skills` | Manage skills from GitHub repos |
| `cmd mods` | Manage mods (npm, git, local paths) |
| `cmd feedback [title]` | Share feedback / report bugs |

## Slash Commands (Interactive)

`/init` (create AGENTS.md), `/import [claude\|codex\|cursor\|pi\|opencode\|gemini]` (import setup from another agent), `/memory`, `/resume`/`/sessions`, `/fork`, `/worktree`, `/clone`, `/rewind`, `/tree`, `/clear`, `/compact`, `/config`, `/context`, `/model`, `/effort`, `/taste`, `/learn-taste`, `/skills`, `/agents`, `/design` (UI design partner), `/mcp`, `/share [gist]`, `/theme`, `/rename`.

## Taste Learning (Differentiator)

Command Code learns your coding taste from repos and from sessions of other agents:

```
terminal(command="cmd taste learn https://github.com/user/repo", workdir="~/project")
terminal(command="cmd learn-taste", workdir="~/project")   # from other agents' sessions (Claude Code, Cursor, ...)
```

For fully automated runs, use `--skip-onboarding` so the taste prompt never blocks.

## Procedure

1. Verify readiness: `cmd --version`, `cmd status`.
2. For bounded tasks, use `cmd -p '...'` with `--skip-onboarding` and a `--max-turns` cap (no pty needed).
3. For iterative tasks, start `cmd '...'` with `background=true, pty=true`.
4. Monitor long tasks with `process(action="poll"|"log")`.
5. If it asks for input, respond via `process(action="submit", ...)`.
6. Exit with `process(action="write", data="\x03")` or `process(action="kill")`.
7. Summarize file changes, test results, and next steps back to the user.

## Parallel Work Pattern

Use separate worktrees to avoid collisions:

```
terminal(command="cmd -p 'Fix issue #101 and commit' -w fix-101", workdir="~/project", background=true, pty=true)
terminal(command="cmd -p 'Add regression tests and commit' -w tests-102", workdir="~/project", background=true, pty=true)
process(action="list")
```

## Pitfalls

- The binary is `cmd`, not `code` — easy to confuse with VS Code's CLI.
- `--max-turns` cap-hit exits with code 8 — check exit codes in `-p` mode.
- Onboarding (taste learning) can block automated runs — always pass `--skip-onboarding` for scripts.
- Command Code auto-updates in the background; use `--no-auto-update` for reproducible runs.
- Interactive sessions require `pty=true`; `-p` print mode does NOT need pty.
- Parallel sessions should never share one working directory — use `--worktree` or separate dirs.
- If a session looks stuck, inspect logs before killing: `process(action="log", session_id="<id>")`.

## Verification

Smoke test:

```
terminal(command="cmd -p 'Respond with exactly: CMD_SMOKE_OK' --skip-onboarding --max-turns 5")
```

Success criteria:
- Output includes `CMD_SMOKE_OK`
- Command exits without auth/model errors
- For code tasks: expected files changed and tests pass

## Rules

1. Prefer `cmd -p` for one-shot automation — simpler, no pty needed.
2. Always pass `--skip-onboarding` and a `--max-turns` cap for autonomous runs.
3. Use interactive background mode only when iteration is needed.
4. Always scope sessions to a single repo/workdir or an isolated worktree.
5. For long tasks, provide progress updates from `process` logs.
6. Report concrete outcomes (files changed, tests, remaining risks).
