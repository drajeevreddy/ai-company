---
name: october-canvas-bus
description: "Use when wiring October canvas bus tools into Hermes."
version: 1.0.0
metadata:
  hermes:
    tags: [october, mcp, plugin, capabilities, canvas, multi-agent]
    requires_tools: [terminal, read_file]
---

# October canvas bus in Hermes

October ships an auto-generated bridge at `~/.hermes/plugins/october-bus/` and injects
`OCTOBER_BUS_PORT`, `OCTOBER_BUS_CANVAS`, `OCTOBER_BUS_NODE`, `OCTOBER_BUS_TOKEN`,
`OCTOBER_BUS_MCP_CAPABILITY` into every terminal it spawns. Those env vars are the ONLY thing that
activates the bridge — `plugin.yaml`'s `requires_env` is metadata, the real gate is in `register()`.

That bridge is the correct path to canvas tools: `message_peer`, `check_inbox`, `list_peers`,
`add_terminal`, `add_chat`, `message_child`, `get_node_status`, `create_plan`, `browser_*`, and ~66
more, all named `mcp__october_bus__<tool>` in toolset `mcp-october_bus`.

## The trap: tool registration is capability-gated

The bridge registers its tools from `register(ctx)` -> `ctx.register_tool(...)`, which requires the
`tools.override` capability. Without a grant, plugin load is silent and the agent gets ZERO October
tools with only this in `~/.hermes/logs/agent.log`:

```
capability_check plugin=october-bus capability=tools.override decision=deny checked_by=plugin_capability_granted evidence=not granted
```

Grant it (config, never hand-edit the YAML):

```bash
hermes config set plugins.entries.october-bus.granted_capabilities '["tools.override"]'
```

`hermes plugins capabilities` will still print `declared: (none)` — the grant works anyway, because
`plugin_capability_granted()` reads only `plugins.entries.<id>.granted_capabilities` (or the legacy
`allow_tool_override: true`). Verify with the real check, not the manifest:

```bash
cd ~/.hermes/hermes-agent && ./venv/bin/python -c \
  "import sys;sys.path.insert(0,'.');from hermes_cli.plugin_capabilities import plugin_capability_granted as g;print(g('october-bus','tools.override'))"
```

## Do NOT add `october-bus-mcp` as an mcp_servers entry

`~/.local/bin/october-bus-mcp` is a *different* bus: the standalone `october-bus` daemon (default
port 45457, scope credential at `~/.config/october-bus/<scope>.scope-token`). It is not the canvas
bus — its `list_peers` shows only agents linked via `--connect-to`, never canvas nodes.

Worse, registering it as server name `october-bus` collides with the plugin toolset: identical
normalized names (`mcp__october_bus__message_peer`, ...), and the plugin wins, so Hermes logs
`already owned by MCP toolset 'mcp-october_bus' — skipping to preserve the existing owner` for 9 of
the 11 tools. Use `hermes mcp remove october-bus` if it was added.

## Reaching agents you are NOT wired to

`message_peer` only reaches peers connected to YOU. In a pipeline wired Orion -> Apollo -> Juno ->
Athena, Orion's `list_peers` shows Apollo alone, and `message_peer(peer="Juno")` fails with
`Could not send: no connected peer matches "Juno"` even though Juno is live on the canvas.

Do not fall back on asking an intermediate agent to relay: in practice relays silently drop the
handoff, and the downstream agent stays idle while you assume it is working.

Drive the target directly instead:

`send_to_node(id=<node id from list_canvas>, text=...)`

It hands text to any canvas node — terminal, chat, video editor, slide deck — queuing it for a busy
terminal rather than typing over the session, and reports `delivered now` or `queued`. Note also that
`message_peer` results say `Queued for <peer>; receipt is not confirmed` even on success, so treat a
peer's reply as the only proof it was received.

Keep long briefs in a file in the shared working directory and send ONE LINE pointing at it. A relay
or a queued message then never has to carry the payload verbatim, and the receiving agent reads the
same file you wrote.

## Verify end to end

Restart the harness (tools register at process start; there is no hot reload). Then, from a session
inside an October-spawned terminal:

```bash
hermes chat -q 'Call mcp__october_bus__list_peers with no arguments, then output the raw result.'
```

Real bus output looks like `- Juno (terminal; live)`. Cross-check the log for the executed call —
the model's self-report is not evidence:

```bash
grep -a "tool mcp__october_bus" ~/.hermes/logs/agent.log | tail
# tool mcp__october_bus__list_peers completed (0.01s, 23 chars)
```

## Reading the bus without Hermes

When a tool is unavailable (or to debug the bridge), speak MCP over HTTP directly: POST
`tools/list` to `http://127.0.0.1:$OCTOBER_BUS_PORT/mcp` with headers `X-October-Canvas`,
`X-October-Node`, `X-October-MCP-Capability`. `Accept: application/json, text/event-stream` is
required, and the reply may be an SSE frame — unwrap the `data:` lines before parsing. Never print
`OCTOBER_BUS_TOKEN`.

## Pitfalls

- A `hermes chat -q` child inherits the parent terminal's env, so it sees the canvas bus even when
the parent session does not. Do not conclude the parent is wired from a child's success.
- `execute_code`'s kernel does NOT inherit `OCTOBER_BUS_*`; run bus probes through `terminal`.
- Two live Hermes processes each spawn their own bridge. Leave the wrapper's per-launch agent id
alone (`OCTOBER_BUS_MCP_AGENT_ID` default `command-code-$$`); a fixed id retires the other
process's execution. Set `OCTOBER_BUS_MCP_AGENT_NAME` instead if the display name matters.
