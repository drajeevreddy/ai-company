# MCP server gotchas

Building an MCP **server** that other people's CLIs connect to. These are the ones that make every single call fail while the server looks healthy, or make the client hang with no error at all.

Verify the version you adopt first — `@modelcontextprotocol/sdk` is MIT, Node ≥18, and declares a `zod` peer range (`^3.25 || ^4.0` at the time of writing). A project pinned to an older `zod` 3.x will still resolve, but check rather than assume.

## 1. Registering a tool without `inputSchema` sends the SDK's own context as the arguments

This is the one that wastes an afternoon. With no `inputSchema`, the SDK treats the tool as taking no arguments and passes **its own context object** as the first handler parameter. Your handler receives:

```
{ signal, sessionId, _meta, sendNotification, sendRequest, … }
```

so every declared field is `undefined`, and every call fails validation for reasons that have nothing to do with the client. Passing a schema fixes the calling convention:

```ts
server.registerTool('thing_do', { description: '…', inputSchema: ThingInput.shape }, handler);
```

If a schema has an object-level `.refine()`, it is a `ZodEffects` with no `.shape` — move that rule into the handler and keep the object plain.

## 2. Even then, do not strict-parse the raw arguments

Because of #1 the argument object can arrive with extra SDK keys merged in. A `.strict()` parse of it rejects every call. Pick the keys your schema declares, **then** parse strictly:

```ts
const shape = schema.shape ?? {};
const picked = Object.fromEntries(Object.entries(args ?? {}).filter(([k]) => k in shape));
const parsed = schema.safeParse(picked);   // strictness still applied to what matters
```

The SDK's own shape check is loose, so this second pass is the real validation.

## 3. Stateless Streamable HTTP needs `sessionIdGenerator: undefined` explicitly

Omitting the key does **not** mean stateless — it defaults to stateful, and if you build one server+transport per request (the usual stateless pattern, and the right one when identity comes from a bearer token) then the first call creates a session the second call cannot find. The client hangs, printing nothing.

```ts
new StreamableHTTPServerTransport({ enableJsonResponse: true, sessionIdGenerator: undefined })
```

The SDK types that key as `() => string`, so with `exactOptionalPropertyTypes` you need a cast — that is an interop seam, not a reason to loosen your own types.

## 4. A hanging client prints nothing; wrap every call in a timeout

Symptom #3 appeared as a test file that sat at `TAP version 13` and reported no result ever. Any stall in a protocol test must become a named failure:

```ts
await Promise.race([client.callTool({ name, arguments }), timeoutAfter(8000, name)]);
```

## 5. Reuse one token verifier across transports

If the same credential also authenticates a WebSocket (or REST), extract `verifyToken` into one shared function and call it from both. Two copies is how one surface ends up accepting a token the other rejects. Take the token from an `Authorization` header — never a query string, which leaks into proxy logs.

## 6. Fail closed on auth, and test the refusals

Assert that: a malformed token is refused, an expired one is refused, an unrelated credential type (a service token, a cookie) is refused, and a token for another workspace is refused. These are cheap tests and they are the ones that catch a refactor opening a hole.

## 7. Test the protocol with the real client, not a mock

The four defects above are **invisible to a test that calls your handler directly** — they live in the calling convention and the transport. Drive the real client library against the real server over its real transport. That is what turns "it should work" into "it works", and it caught every one of these.

## 8. Model the pull/push difference in your state machine

A client that *pulls* work is not a client you *push* to. If your dispatch path only marks work "sent" when a push succeeds, pulled work sits in the pre-send state forever and can never be claimed. Give the pull path its own transition (here: `queued → dispatched → running`), so the state machine, the audit trail and the UI stay identical for both.

See also: [[Skills/software-development|software-development]] · [[Skills/verify-by-running-it|verify-by-running-it]]
