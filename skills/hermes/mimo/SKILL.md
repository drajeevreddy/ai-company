---
name: mimo
description: "Delegate coding to mimocode CLI (features, fixes, PRs)."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Coding-Agent, Mimocode, Mimo, Autonomous, Refactoring]
    related_skills: [claude-code, codex, opencode, cursor-agent, vibe, command-code, hermes-agent]
---

# mimocode CLI (`mimo`)

Use [mimocode](https://mimocode.dev) as an autonomous coding worker orchestrated by Hermes terminal/process tools. `mimo` is a TUI-based AI coding agent with one-shot `run`, a headless `serve` mode, and session export/import.

## When to Use

- User explicitly asks to use mimocode / mimo
- You want an external coding agent to implement/refactor/review code
- You need a headless server you can attach to from multiple clients
- You want session export/import or token/cost stats

## Prerequisites

- Installed under `~/.mimocode/bin/` (binary `mimo`); install via `mimo upgrade` or the mimocode installer
- Verify: `mimo --version`
- Auth: `mimo providers` (alias `mimo auth`) — manage AI providers and credentials
- Git repository for code tasks (recommended)
- `pty=true` for interactive TUI sessions

## Binary Resolution (Important)

The binary is `mimo`, located at `~/.mimocode/bin/mimo`. If `mimo` is not on PATH:

```
terminal(command="export PATH=\"$HOME/.mimocode/bin:$PATH\"")
terminal(command="ls ~/.mimocode/bin/")
```

## One-Shot Tasks (`mimo run`)

Use `mimo run` for bounded, non-interactive tasks:

```
terminal(command="mimo run 'Add retry logic to API calls and update tests'", workdir="~/project")
```

Attach files and get JSON output:

```
terminal(command="mimo run 'Review this config for security issues' -f config.yaml -f .env.example --format json", workdir="~/project")
```

Force a model, reasoning variant, and thinking blocks:

```
terminal(command="mimo run 'Debug why tests fail in CI' -m provider/model --variant high --thinking", workdir="~/project")
```

Auto-approve permissions (dangerous — use sparingly):

```
terminal(command="mimo run 'Refactor the parser module and run tests' --dangerously-skip-permissions", workdir="~/project")
```

## Interactive Sessions (TUI, Background)

For iterative work, start the TUI in background:

```
terminal(command="mimo 'Implement OAuth refresh flow and add tests'", workdir="~/project", background=true, pty=true)
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
terminal(command="mimo -c", workdir="~/project", background=true, pty=true)   # Continue last session
terminal(command="mimo -s <session-id>", workdir="~/project", background=true, pty=true)
terminal(command="mimo -c --fork", workdir="~/project", background=true, pty=true)  # Fork when continuing
terminal(command="mimo session", workdir="~/project")   # Manage sessions (list/delete/...)
```

## Headless Server Mode

Start a headless server and attach to it from one-shot runs or the TUI:

```
terminal(command="mimo serve --port 4096", background=true)   # Headless server
# Attach a one-shot run to the running server:
terminal(command="mimo run 'Add pagination to the API client' --attach http://localhost:4096", workdir="~/project")
# Attach the TUI:
terminal(command="mimo attach http://localhost:4096", background=true, pty=true)
# Remote dir override when attaching:
terminal(command="mimo run 'Run the test suite' --attach http://localhost:4096 --dir /srv/project", workdir="~/project")
```

Server flags: `--port`, `--hostname` (default 127.0.0.1), `--mdns` (service discovery), `--no-auth` (DANGEROUS, non-loopback), `--cors`. Basic auth via `-p/--password` or `MIMOCODE_SERVER_PASSWORD` env.

## PR Workflow

```
terminal(command="mimo pr 42", workdir="~/project", pty=true)   # Fetch + checkout PR branch, then run mimo
```

## Common Flags

| Flag | Use |
|------|-----|
| `mimo run 'msg'` | One-shot execution and exit |
| `-m, --model provider/model` | Force specific model |
| `--variant <level>` | Model variant / reasoning effort (high, max, minimal) |
| `--thinking` | Show thinking blocks |
| `-f, --file <path>` | Attach file(s) (repeatable) |
| `--format default\|json` | Output format (json = raw event stream) |
| `--agent <name>` | Agent to use |
| `--dangerously-skip-permissions` | Auto-approve permissions (dangerous) |
| `-c, --continue` | Continue last session |
| `-s, --session <id>` | Continue specific session |
| `--fork` | Fork session before continuing |
| `--attach <url>` | Attach to running server |
| `--dir <path>` | Directory to run in (remote path if attaching) |
| `--share` | Share the session |
| `--title <name>` | Session title |

## Subcommands

| Command | Use |
|---------|-----|
| `mimo providers` / `auth` | Manage AI providers and credentials |
| `mimo models [provider]` | List all available models |
| `mimo agent` | Manage agents |
| `mimo session` | Manage sessions |
| `mimo serve` | Headless server (attach with `mimo attach <url>`) |
| `mimo run [message..]` | One-shot run |
| `mimo pr <number>` | Checkout PR branch then run |
| `mimo stats` | Token usage and cost statistics |
| `mimo export [sessionID]` | Export session data as JSON |
| `mimo import <file>` | Import session data from JSON file or URL |
| `mimo mcp` | Manage MCP servers |
| `mimo acp` | Start ACP (Agent Client Protocol) server |
| `mimo plugin <module>` | Install plugin and update config |
| `mimo github` | Manage GitHub agent |
| `mimo upgrade [target]` | Upgrade mimocode |
| `mimo uninstall` | Uninstall and remove related files |
| `mimo debug` | Debugging and troubleshooting tools |
| `mimo completion` | Shell completion script |

## Procedure

1. Verify readiness: `mimo --version`, `mimo providers list` (or `mimo models`).
2. For bounded tasks, use `mimo run '...'` (no pty needed).
3. For iterative tasks, start `mimo '...'` with `background=true, pty=true`.
4. For multi-client or remote work, use `mimo serve` + `--attach`.
5. Monitor long tasks with `process(action="poll"|"log")`.
6. If it asks for input, respond via `process(action="submit", ...)`.
7. Exit with `process(action="write", data="\x03")` or `process(action="kill")`.
8. Summarize file changes, test results, and next steps back to the user.

## Parallel Work Pattern

Use separate workdirs to avoid collisions:

```
terminal(command="mimo run 'Fix issue #101 and commit'", workdir="/tmp/issue-101", background=true, pty=true)
terminal(command="mimo run 'Add parser regression tests and commit'", workdir="/tmp/issue-102", background=true, pty=true)
process(action="list")
```

## Pitfalls

- Interactive TUI sessions require `pty=true`; `mimo run` does NOT need pty.
- `--dangerously-skip-permissions` is dangerous — never use it for unknown/untrusted code.
- The headless server binds to 127.0.0.1 by default; `--no-auth` on non-loopback is DANGEROUS.
- PATH may not include `~/.mimocode/bin` — resolve with an explicit path if needed.
- Parallel sessions should never share one working directory.
- If a session looks stuck, inspect logs before killing: `process(action="log", session_id="<id>")`.

## Verification

Smoke test:

```
terminal(command="mimo run 'Respond with exactly: MIMO_SMOKE_OK'")
```

Success criteria:
- Output includes `MIMO_SMOKE_OK`
- Command exits without provider/model errors
- For code tasks: expected files changed and tests pass

## Rules

1. Prefer `mimo run` for one-shot automation — simpler, no pty needed.
2. Use interactive background mode only when iteration is needed.
3. Use `mimo serve` + `--attach` when multiple clients or remote access is needed.
4. Always scope sessions to a single repo/workdir.
5. For long tasks, provide progress updates from `process` logs.
6. Report concrete outcomes (files changed, tests, remaining risks).
