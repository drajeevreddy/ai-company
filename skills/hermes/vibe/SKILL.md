---
name: vibe
description: "Delegate coding to Mistral Vibe CLI (features, fixes, PRs)."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Coding-Agent, Mistral, Vibe, Autonomous, Refactoring]
    related_skills: [claude-code, codex, command-code, cursor-agent, hermes-agent, mimo, opencode]
---

# Mistral Vibe CLI

Use [Mistral Vibe](https://github.com/mistralai/vibe) as an autonomous coding worker orchestrated by Hermes terminal/process tools. `vibe` is Mistral's agentic coding CLI with an interactive session and a programmatic one-shot mode.

## When to Use

- User explicitly asks to use Vibe / Mistral Vibe
- You want an external coding agent to implement/refactor/fix code
- You need long-running sessions with progress checks
- You want cost/token-bounded runs (`--max-price`, `--max-tokens`)

## Prerequisites

- Installed via uv: `uv tool install mistral-vibe` → binary `vibe` (and `vibe-acp`) on PATH
- Verify: `vibe --version`
- Auth: run `vibe` once interactively (or `vibe --setup`) to log in / configure the provider
- Git repository for code tasks (recommended)
- `pty=true` for interactive sessions

## Binary Resolution (Important)

The binary is `vibe` (package name is `mistral-vibe`). If `vibe` is not on PATH:

```
terminal(command="uv tool install mistral-vibe")           # install/repair
terminal(command="ls ~/.local/share/uv/tools/mistral-vibe/bin/")
terminal(command="uv tool run mistral-vibe --version")     # run without installing
```

## One-Shot Tasks (Programmatic Mode)

Use `-p, --prompt` for bounded, non-interactive tasks:

```
terminal(command="vibe -p 'Add retry logic to API calls and update tests'", workdir="~/project")
```

Bounded runs — interrupt automatically on turn/cost/token limits:

```
terminal(command="vibe -p 'Implement OAuth refresh flow' --max-turns 30 --max-price 2.00 --max-tokens 200000", workdir="~/project")
```

Machine-readable output:

```
terminal(command="vibe -p 'Refactor auth module' --output json", workdir="~/project")
terminal(command="vibe -p 'Fix the flaky test' --output streaming", workdir="~/project")   # NDJSON per message
```

## Tool Control

In programmatic mode, `--enabled-tools` restricts to exactly those tools (others disabled). Patterns: exact names, globs, or `re:` regexes:

```
terminal(command="vibe -p 'Run the test suite and report' --enabled-tools 'bash*'", workdir="~/project")
terminal(command="vibe -p 'Update the README' --enabled-tools 'edit*' 'write*' --disabled-tools 're:.*(rm|delete).*'", workdir="~/project")
```

## Agents & Approval

Builtin agents: `default`, `plan` (read-only planning), `accept-edits`, `auto-approve`; custom agents live in `~/.vibe/agents/NAME.toml`:

```
terminal(command="vibe -p 'Analyze the codebase and propose a migration plan' --agent plan", workdir="~/project")
terminal(command="vibe -p 'Refactor the parser module and run tests' --agent auto-approve", workdir="~/project")
# --auto-approve / --yolo also allow all tool calls directly
```

## Interactive Sessions (Background)

For iterative work, start the interactive session in background:

```
terminal(command="vibe 'Implement OAuth refresh flow and add tests'", workdir="~/project", background=true, pty=true)
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

### Resuming Sessions

```
terminal(command="vibe -c", workdir="~/project", background=true, pty=true)              # Continue last session
terminal(command="vibe --resume <SESSION_ID>", workdir="~/project", background=true, pty=true)
```

## Common Flags

| Flag | Use |
|------|-----|
| `-p, --prompt [TEXT]` | Programmatic mode: send prompt, print response, exit |
| `--max-turns N` | Max assistant turns (programmatic mode only) |
| `--max-price DOLLARS` | Max cost; interrupts session when exceeded |
| `--max-tokens N` | Max total prompt+completion tokens; interrupts when exceeded |
| `--enabled-tools TOOL` | Enable only these tools (exact/glob/`re:`); repeatable |
| `--disabled-tools TOOL` | Disable tools after enabled-filtering; repeatable |
| `--output text\|json\|streaming` | Output format (programmatic mode) |
| `--agent NAME` | Agent: `default`, `plan`, `accept-edits`, `auto-approve`, or `~/.vibe/agents/NAME.toml` |
| `--auto-approve` | Allow all tool calls (also `--yolo`) |
| `-c` / `--resume [SESSION_ID]` | Continue last / specific session |
| `--workdir DIR` | Working directory |
| `--worktree NAME` | Run in a git worktree |
| `--add-dir DIR` | Add extra workspace directory (repeatable) |
| `--trust` | Trust the workspace without prompting |
| `--setup` | Run setup / configure |
| `--check-upgrade` | Check for upgrades |

## Procedure

1. Verify readiness: `vibe --version`.
2. For bounded tasks, use `vibe -p '...'` (no pty needed). Add `--max-price`/`--max-tokens` to cap spend.
3. Restrict tools with `--enabled-tools` when the task is narrow (safer in programmatic mode).
4. For iterative tasks, start `vibe '...'` with `background=true, pty=true`.
5. Monitor long tasks with `process(action="poll"|"log")`.
6. If it asks for input, respond via `process(action="submit", ...)`.
7. Exit with `process(action="write", data="\x03")` or `process(action="kill")`.
8. Summarize file changes, test results, and next steps back to the user.

## Parallel Work Pattern

Use separate workdirs/worktrees to avoid collisions:

```
terminal(command="vibe -p 'Fix issue #101 and commit' --worktree fix-101", workdir="~/project", background=true, pty=true)
terminal(command="vibe -p 'Add regression tests and commit' --worktree tests-102", workdir="~/project", background=true, pty=true)
process(action="list")
```

## Pitfalls

- Interactive sessions require `pty=true`; `-p` programmatic mode does NOT need pty.
- `--max-turns`, `--max-price`, `--max-tokens` only apply in programmatic mode (`-p`).
- Binary is `vibe`, not `mistral-vibe` — the package name and binary name differ.
- Custom agents live in `~/.vibe/agents/NAME.toml`; tool-approval behavior follows the selected agent's config.
- Parallel sessions should never share one working directory — use `--worktree` or separate dirs.
- If a session looks stuck, inspect logs before killing: `process(action="log", session_id="<id>")`.

## Verification

Smoke test:

```
terminal(command="vibe -p 'Respond with exactly: VIBE_SMOKE_OK' --max-price 0.10")
```

Success criteria:
- Output includes `VIBE_SMOKE_OK`
- Command exits without auth/model errors
- For code tasks: expected files changed and tests pass

## Rules

1. Prefer `vibe -p` for one-shot automation — simpler, no pty needed.
2. Always set `--max-price` (and/or `--max-tokens`) for autonomous programmatic runs.
3. Use interactive background mode only when iteration is needed.
4. Always scope sessions to a single repo/workdir or an isolated worktree.
5. For long tasks, provide progress updates from `process` logs.
6. Report concrete outcomes (files changed, tests, remaining risks).
