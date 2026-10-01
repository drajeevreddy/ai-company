# Verifying MCP endpoints from the shell

Use these when the agent's own session cannot exercise the new tools (they load only at startup), or when you need to confirm the *token* works rather than just the client.

All recipes assume `URL=https://host/mcp`. Streamable HTTP requires the SSE-capable `Accept` header — without it the server may answer with a non-JSON error.

## 1. Auth probe (before configuring anything)

```bash
curl -s -i -X POST "$URL" \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"hermes","version":"1.0"}}}'
```

Read the status line and headers:

| Result | Meaning | Next |
|---|---|---|
| 200 + tools JSON | anonymous access works | configure without auth |
| 401 + `WWW-Authenticate: Bearer resource_metadata="..."` | OAuth required | fetch the metadata URL, then configure `--auth oauth` |
| 401 + body naming `?api_key=` | vendor offers an API-key fallback | use the query-param form only if OAuth cannot work |
| 404 / connect timeout | wrong path or transport | get the canonical endpoint from vendor docs |

## 2. OAuth discovery

The `resource_metadata` URL from the 401 is the protected-resource document:

```bash
curl -s "https://host/.well-known/oauth-protected-resource/mcp"
# → resource, authorization_servers[], scopes_supported[], bearer_methods_supported
```

Fetch the authorization server's own metadata (the discovery document it advertises, commonly `<authorization_server>/.well-known/oauth-authorization-server`) to get `authorization_endpoint`, `token_endpoint`, `registration_endpoint` and `grant_types_supported`. Confirm `refresh_token` is a supported grant — that is what makes expiry silent.

Hermes performs the dynamic client registration and the PKCE flow itself; this step only tells you what to expect and whether a paste-back fallback will be needed.

## 3. Manual session handshake (proves the stored token)

```bash
TOK=$(python3 -c "import json;print(json.load(open('$HOME/.hermes/mcp-tokens/<name>.json'))['access_token'])")

SID=$(curl -s -D - -o /dev/null -X POST "$URL" \
  -H "Authorization: Bearer $TOK" -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"hermes","version":"1.0"}}}' \
  | grep -i 'mcp-session-id' | tr -d '\r' | awk '{print $2}')

curl -s -X POST "$URL" -H "Authorization: Bearer $TOK" -H "mcp-session-id: $SID" \
  -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","method":"notifications/initialized"}' >/dev/null
```

Then list or call:

```bash
# tools/list
curl -s -X POST "$URL" -H "Authorization: Bearer $TOK" -H "mcp-session-id: $SID" \
  -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list"}'

# tools/call — a read-only probe tool is the cheapest end-to-end proof
curl -s -X POST "$URL" -H "Authorization: Bearer $TOK" -H "mcp-session-id: $SID" \
  -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"health_get","arguments":{}}}'
```

Responses come back as SSE: `event: message` then `data: {...}`. Parse the `data:` line, not the whole body.

## 4. Pitfalls

- Skipping `notifications/initialized` returns `method "tools/call" is invalid during session initialization` — an auth-looking error that is really a protocol-order error.
- The bearer token is short-lived (commonly ~1h). `expires_at` in the token JSON is an epoch timestamp; a 401 mid-probe usually means expiry, not a revoked grant — Hermes refreshes on the next connection.
- Never echo a token into command output. Read it into a shell variable and pass it as a header.
- Piping `curl` straight into an interpreter trips the security scanner and needs approval. Write the response to a file and parse the file when the payload must be processed.
- `mcp-tokens/` is per profile: resolve `$HERMES_HOME` rather than hardcoding `~/.hermes`.
