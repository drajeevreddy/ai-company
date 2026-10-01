---
name: security-tool-integration
description: Add security tools to Hermes Agent and AI clients via MCP.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [security, pentest, mcp, tool-integration, agent-setup]
---

# Security Tool Integration

Install a security/pentesting tool and wire it into the user's AI agent ecosystem (Hermes Agent + Claude Code / Cursor / Codex / VS Code) as an MCP server.

Scope: this skill covers a **local** tool that ships its own `mcp` subcommand. For vendor-hosted **remote** servers that need OAuth or a bearer key, follow `mcp-server-integration` instead — it owns the interactive `hermes mcp add` flow, token storage, and out-of-band verification, and its tool-count and restart rules apply here too.

## Procedure

### 1. Inspect the tool before installing

Read the repo's README and packaging files to understand what the tool does, how it ships, and whether it has a built-in MCP server.

```bash
# Clone first either way — the README, pyproject and action.yml tell you how
# the tool ships and what its MCP subcommand is called, which a wheel install
# alone does not give you:
git clone --depth 1 <repo> /tmp/<tool>-src
# If a PyPI package exists:
pip install <tool>
# If only a GitHub source:
cd /tmp/<tool>-src && pip install -e .
# Verify the binary is on PATH:
which <tool> && <tool> --version
```

Look for an `action.yml`, `Dockerfile`, or a `<tool> mcp` / `<tool> setup --mcp` subcommand — these signal native MCP support.

### 2. Check MCP capability

Most tools that ship an MCP server expose it through a subcommand. Test with `--dry-run` first to see config changes without applying them.

```bash
<tool> setup --mcp --dry-run
# or:
<tool> mcp --help
```

### 3. Configure external AI clients (one-shot)

If the tool offers an `--auto-inject` or `--mcp` setup wizard, run it to write configs for Claude Desktop, Cursor, and VS Code simultaneously.

```bash
<tool> setup --mcp --auto-inject
```

This writes to `~/.claude/claude_desktop_config.json`, `~/.cursor/mcp.json`, and `~/.vscode/mcp.json` in one step.

### 4. Configure Hermes Agent

Add the MCP server entry to `~/.hermes/config.yaml` using `hermes config set` with a JSON value. The key is `mcp_servers`.

```bash
hermes config set mcp_servers '{"<server-name>": {"command": "<binary>", "args": ["mcp"], "timeout": 300, "connect_timeout": 120}}'
```

Use `hermes config set --force` if the running Hermes version does not recognize the `mcp_servers` key (the value is saved either way).

### 5. Verify

Confirm the server is registered and enabled:

```bash
hermes mcp list
```

Expected output: server name, transport, tool count, and `✓ enabled`.

### 6. Restart Hermes Agent

MCP tools are discovered at startup. Exit and relaunch Hermes for the new tools to appear. After restart, the tools are callable as `mcp_<server-name>_<tool-name>`.

## Pitfalls

- **File-write tools cannot edit `~/.hermes/config.yaml`.** `write_file` and `patch` are refused by design, because Hermes treats its own config as security-sensitive ("Agent cannot modify security-sensitive configuration"). Escalate straight to `hermes config set` for step 4 — do not spend a call attempting a direct edit, and do not try to route around the guard by writing the file some other way.
- **`command` must be on PATH.** Before configuring, run `which <binary>` to confirm the install location is in the default PATH that Hermes inherits. A `command not found` at connection time fails silently — the server shows as failed in `hermes mcp list` with no tools discovered.
- **`hermes config set` takes JSON, not dotted keys.** Nested structures like `mcp_servers.pentest-ai.command` are not supported. Pass the full JSON object as the value: `hermes config set mcp_servers '{...}'`.
- **`--auto-inject` only writes external client configs.** It does NOT touch `~/.hermes/config.yaml`. You must always run step 4 separately for Hermes Agent.
- **MCP tools appear only after restart.** `hermes mcp list` shows the config entry immediately, but the actual tool discovery and registration happens at Hermes startup. Do not assume tools are live until you have restarted.
- **Verify with `hermes mcp list`, not just config write.** A successful `hermes config set` only confirms the key was written. `hermes mcp list` confirms the server connected and tools were discovered.
