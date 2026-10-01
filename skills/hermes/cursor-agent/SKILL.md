---
name: cursor-agent
description: "Delegate coding to Cursor Agent CLI (features, PRs, fixes)."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Coding-Agent, Cursor, Autonomous, Refactoring, Code-Review]
    related_skills: [claude-code, codex, command-code, hermes-agent, mimo, opencode, vibe]
---

# Cursor Agent CLI

Use [Cursor Agent](https://cursor.com) as an autonomous coding worker orchestrated by Hermes terminal/process tools. Cursor's headless agent CLI runs in the terminal (TUI or print mode) with the same model backend as the Cursor IDE.

## When to Use

- User explicitly asks to use Cursor / Cursor Agent
- You want an external coding agent to implement/refactor/review code
- You need long-running sessions with progress checks
- You want parallel task execution in isolated workdirs/worktrees

## Prerequisites

- Installed: `cursor-agent` (also invoked as `agent`). Ships as a symlink under `~/.local/share/cursor-agent/versions/<ver>/cursor-agent` (e.g. installed via the Cursor Agent install script).
- Auth configured: `cursor-agent login` (set `NO_OPEN_BROWSER=1` to skip browser opening) — verify with `cursor-agent status` / `cursor-agent whoami`
- Git repository for code tasks (recommended)
- `pty=true` for interactive TUI sessions

## Binary Resolution (Important)

`cursor-agent` and `agent` are the same binary (`CURSOR_INVOKED_AS` tells it how it was called). If behavior differs between your terminal and Hermes:

```
terminal(command="which -a cursor-agent agent")
terminal(command="cursor-agent --version")
```

## One-Shot Tasks (Print Mode)

Use `-p, --print` for bounded, non-interactive tasks. Print mode has access to all tools, including write and shell:

```
terminal(command="cursor-agent -p 'Add retry logic to API calls and update tests'", workdir="~/project")
```

Machine-readable output with `--output-format`:

```
terminal(command="cursor-agent -p 'Refactor auth module' --output-format json", workdir="~/project")
terminal(command="cursor-agent -p 'Fix the flaky test' --output-format stream-json --stream-partial-output", workdir="~/project")
```

Read-only planning / Q&A modes (no edits):

```
terminal(command="cursor-agent -p 'Analyze this codebase and propose a plan' --mode plan", workdir="~/project")
terminal(command="cursor-agent -p 'Explain how auth works here' --mode ask", workdir="~/project")
# --plan is shorthand for --mode=plan
```

Force a specific model (list with `cursor-agent --list-models` or `cursor-agent models`):

```
terminal(command="cursor-agent -p 'Add pagination to the API client' --model gpt-5.3-codex", workdir="~/project")
# Parameterized models accept bracket overrides:
# --model 'claude-opus-4-8[context=1m,effort=high,fast=false]'
```

## Interactive Sessions (Background)

For iterative work, start the agent in background with a pty:

```
terminal(command="cursor-agent 'Implement OAuth refresh flow and add tests'", workdir="~/project", background=true, pty=true)
# Returns session_id

# Send a prompt / follow-up
process(action="submit", session_id="<id>", data="Now add error handling for token expiry")

# Monitor progress
process(action="poll", session_id="<id>")
process(action="log", session_id="<id>")

# Exit cleanly — Ctrl+C, or kill
process(action="write", session_id="<id>", data="\x03")
process(action="kill", session_id="<id>")
```

### Resuming Sessions

```
terminal(command="cursor-agent ls")                       # List chat sessions
terminal(command="cursor-agent resume")                   # Resume latest chat
terminal(command="cursor-agent --continue", workdir="~/project", background=true, pty=true)
terminal(command="cursor-agent --resume <chatId>", workdir="~/project", background=true, pty=true)
```

## Common Flags

| Flag | Use |
|------|-----|
| `-p, --print` | Non-interactive print mode (scripts). All tools available |
| `--output-format text\|json\|stream-json` | Output format (only with `--print`) |
| `--mode plan\|ask` | Read-only planning / Q&A mode |
| `--model <name>` | Force a model (`cursor-agent models` to list) |
| `--continue` | Continue previous session |
| `--resume [chatId]` | Resume a specific session |
| `--workspace <path-or-name>` | Workspace dir (defaults to cwd) |
| `--add-dir <path>` | Add extra workspace root (repeatable) |
| `-w, --worktree [name]` | Isolated git worktree at `~/.cursor/worktrees/<reponame>/<name>` |
| `--worktree-base <branch>` | Branch/ref to base the worktree on |
| `--yolo` / `-f` | Force allow commands unless explicitly denied |
| `--auto-review` | Server classifier auto-runs safe tool calls, prompts for the rest |
| `--sandbox enabled\|disabled` | Override sandbox mode |
| `--approve-mcps` | Auto-approve all MCP servers |
| `--trust` | Trust the workspace without prompting |
| `--api-key <key>` | Auth key (or `CURSOR_API_KEY` env) |
| `-e, --endpoint <url>` | API endpoint (or `CURSOR_API_ENDPOINT` env; default `https://api2.cursor.sh`) |

## Subcommands

| Command | Use |
|---------|-----|
| `login` / `logout` | Auth (browser-based; `NO_OPEN_BROWSER=1` to suppress) |
| `status` / `whoami` | Auth status |
| `models` | List available models for the account |
| `mcp` | Manage MCP servers |
| `plugin` | Manage plugins and plugin marketplaces |
| `worker` | Start a private cloud worker |
| `create-chat` | Create an empty chat, return its ID |
| `generate-rule` / `rule` | Generate a Cursor rule |
| `ls` / `resume` | List / resume chat sessions |
| `update` | Self-update to latest version |
| `about` | Version, system, account info |

## Procedure

1. Verify readiness: `cursor-agent --version`, `cursor-agent status`.
2. For bounded tasks, use `cursor-agent -p '...'` (no pty needed; add `--output-format json` for machine-readable).
3. For iterative tasks, start `cursor-agent '...'` with `background=true, pty=true`.
4. Monitor long tasks with `process(action="poll"|"log")`.
5. If it asks for input, respond via `process(action="submit", ...)`.
6. Exit with `process(action="write", data="\x03")` or `process(action="kill")`.
7. Summarize file changes, test results, and next steps back to the user.

## Parallel Work Pattern

Use separate workdirs/worktrees to avoid collisions:

```
terminal(command="cursor-agent -p 'Fix issue #101 and commit' --worktree fix-101", workdir="~/project", background=true, pty=true)
terminal(command="cursor-agent -p 'Add parser regression tests and commit' --worktree tests-102", workdir="~/project", background=true, pty=true)
process(action="list")
```

## Pitfalls

- Interactive TUI sessions require `pty=true`; `-p` print mode does NOT need pty.
- `agent` and `cursor-agent` are the same binary — don't double-check both; pick one for `which`.
- Model names are account-specific: always check `cursor-agent models` before pinning `--model`.
- Parallel sessions should never share one working directory — use `--worktree` or separate dirs.
- If a session looks stuck, inspect logs before killing: `process(action="log", session_id="<id>")`.
- Worktrees land under `~/.cursor/worktrees/`, not in the repo — remember to clean them up after merging.

## Verification

Smoke test:

```
terminal(command="cursor-agent -p 'Respond with exactly: CURSOR_SMOKE_OK'")
```

Success criteria:
- Output includes `CURSOR_SMOKE_OK`
- Command exits without auth/model errors
- For code tasks: expected files changed and tests pass

## Rules

1. Prefer `cursor-agent -p` for one-shot automation — simpler, no pty needed.
2. Use interactive background mode only when iteration is needed.
3. Always scope sessions to a single repo/workdir or an isolated worktree.
4. For long tasks, provide progress updates from `process` logs.
5. Report concrete outcomes (files changed, tests, remaining risks).
