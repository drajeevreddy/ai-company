---
name: mcp-server-integration
description: "Use when adding or verifying an MCP server."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [mcp, tool-integration, oauth, verification, agent-setup, hermes]
    related_skills: [hermes-agent, security-tool-integration]
    requires_tools: [terminal]
    requires_toolsets: [terminal]
    editorial_name: MCP Server Integration
    editorial_description: Connect a remote (HTTP) or local (stdio) MCP server to Hermes end to end — catalog preset or manual add, OAuth or bearer auth, token storage, and an out-of-band live call that proves the tools work.
---

# MCP Server Integration

The class of task: take an MCP server (a vendor-hosted remote endpoint, or a local stdio command) and make its tools usable in Hermes, then prove it works with real output.

The bundled `hermes-agent` skill (`references/native-mcp.md`) owns the config schema, transport keys, and sampling options — read that for the key table. This skill owns the install / authenticate / verify **workflow** and the traps in it, and deliberately does not restate the schema.

## Procedure

### 1. Try the catalog before hand-rolling

```bash
hermes mcp catalog | grep -i <vendor>
hermes mcp install <preset-name>     # one-click; carries url/auth/transport
```

Only fall through to step 2 when the vendor has no preset. Also confirm the name is not already taken (`hermes mcp list`) before adding.

### 2. Probe the endpoint from the shell before touching config

POST a raw `initialize` at the endpoint and read the failure shape (exact curl in `references/verifying-mcp-endpoints.md`):

- **401 + `WWW-Authenticate: Bearer resource_metadata="<url>"`** — OAuth required. Fetch that metadata URL, and the authorization server it names, to learn the scopes and the authorization/token/registration endpoints *before* configuring anything.
- **Error text mentioning a `?api_key=` query parameter** — the vendor documents an API-key fallback for clients that cannot complete OAuth.
- **404 / timeout** — wrong path. Vendors publish the canonical endpoint in their docs; when the extract backend is unavailable, `curl -sL <docs-url>` and strip tags locally rather than guessing. Many docs sites also expose `/llms.txt` listing every page.

### 3. Pick the auth model

Prefer OAuth whenever the server supports it: no secret enters chat or config, and the refresh token means expiry is renewed silently instead of the user re-authenticating. Choose the API-key/query-param fallback only when OAuth genuinely cannot work.

### 4. Install from a tmux session — `hermes mcp add` is interactive

```bash
tmux new-session -d -s mcpadd -x 200 -y 50 "hermes mcp add <name> --url <url> --auth oauth --connect-timeout 180; echo DONE=$?; sleep 600"
sleep 20 && tmux capture-pane -t mcpadd -p | tail -40
```

Handle each prompt as it appears:

- **OAuth:** Hermes opens the browser on the local machine *and* prints the authorize URL with a "paste the redirect URL here" fallback. Relay the URL to the user and wait. Only paste a redirect URL back if their browser could not reach the loopback callback (headless/remote session).
- **Tool selection:** `Enable all N tools? [Y/n/select]` arrives after discovery succeeds — bare `Enter` enables all, `select` opens a curses checklist, `n` discards without saving. Send the key alone (`tmux send-keys -t mcpadd Enter`), then re-capture the pane to confirm the prompt advanced.
- Finish with `tmux kill-session -t mcpadd`.

### 5. Verify with real output, out of band

1. `hermes mcp test <name>` — exit 0 plus the discovered tool list.
2. A live `tools/call` against the endpoint using the stored token (recipe in `references/verifying-mcp-endpoints.md`). Discovery alone proves less than a real call returning real data.
3. Inspect what was actually persisted: OAuth material lives in `$HERMES_HOME/mcp-tokens/<name>.json` (`access_token`, `refresh_token`, `expires_at`) alongside `<name>.client.json` (registered client_id + redirect_uris) and `<name>.meta.json` (endpoints + scopes), all `0600` inside a `0700` directory. A refresh token plus an `offline_access` scope means renewal is automatic.

### 6. Hand over

MCP tools are discovered at agent **startup** — there is no hot reload. Tell the user to start a new session; the running one will never see the new tools. They register as `mcp_<server>_<tool>`.

## Always-on rules

- Config changes go through `hermes mcp add`, `hermes config set`, and `hermes mcp configure`. Never hand-edit `config.yaml`.
- Secrets never enter chat and never land in `config.yaml`. For bearer/API-key servers use `hermes mcp add --auth header`: it prompts with a masked input and stores the token in `.env` as `<SERVER>_API_KEY`, leaving only a header reference in config. Never ask the user to paste a key into the conversation.
- Price the tool count before choosing "enable all". Every MCP tool is injected into every conversation's schema, so a large server is a standing per-call token tax; `hermes mcp configure <name>` toggles individual tools when only some are wanted.
- When the server has write tools (publish, delete, disconnect), name them in the hand-off report — the user needs the blast radius to decide whether to trim.
- Lifecycle commands: `hermes mcp login|reauth <name>`, `hermes mcp remove|rm <name>`, `hermes mcp list`.

## Pitfalls

- **Never run `hermes mcp add` as a plain foreground call.** It blocks on two interactive prompts the user cannot see while the agent holds the call. Run it in tmux (step 4) and drive it with `capture-pane` / `send-keys`.
- **A long authorize URL wraps at the tmux pane width.** Reconstruct it by joining the wrapped lines before relaying it to the user; hand them a spliced link and the login round-trip burns a turn.
- **Do not verify by calling `mcp_<server>_*` in the current session.** Those tool names are not in the running schema yet, so the call fails for a reason unrelated to the install. Use `hermes mcp test` or a raw JSON-RPC call instead.
- **Do not infer success from the installer's exit status.** The add path can report a saved config and still exit non-zero; only `hermes mcp test` / `hermes mcp list` settle it.
- **`tools/call` before the session handshake is rejected** with `method "tools/call" is invalid during session initialization`. Authenticated servers hand back an `mcp-session-id` header on `initialize`; send `notifications/initialized` with that header first.
- **`--env` is rejected for URL servers** — it is stdio-only. Remote servers take `headers` instead, and the CLI wires those from `.env` for you.
- **A connected server that reports zero tools is a failure, not a success.** Re-check the URL path and the auth mode rather than saving it and hoping.
- **Vendor docs beat assumption on endpoint and auth mode** — the same host often serves the REST API at one path and MCP at another (`/v1` vs `/mcp`), and the docs state which auth flows are supported.

## References

- `references/verifying-mcp-endpoints.md` — raw curl recipes: auth probe, OAuth discovery from `WWW-Authenticate`, full session handshake, `tools/list` and `tools/call`.
