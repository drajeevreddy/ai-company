# Container, env and secret gotchas

Small things that cost real hours. Every one of these passes on the host and fails in a container, or the reverse — which is why they survive unit tests. Check these before debugging anything else.

## 1. A strict schema over `process.env` crash-loops every container

`z.object({...}).strict()` parsed against `process.env` rejects the whole environment, because a container always carries `PATH`, `HOME`, `HOSTNAME`, `PWD`, `NODE_VERSION`. Symptom: the service restarts forever with `Unrecognized key(s) in object: 'PATH', 'HOME', …`, and it looks like a config problem in your own vars.

Validate field by field and let unknown keys through. Strictness belongs on wire schemas and request bodies, never on the process environment.

## 2. `z.coerce.boolean()` makes `"false"` true

Any non-empty string is truthy, so `TRUST_PROXY=false` parses as `true`. Use an explicit set and default the unknown case to the safe direction:

```ts
const booleanFromEnv = z.enum(['true','false','1','0','yes','no','on','off'])
  .optional()
  .transform((v) => v === 'true' || v === '1' || v === 'yes' || v === 'on');
```

Do not reach for `.default(false)` on the transformed schema — with `exactOptionalPropertyTypes` the default must match the *input* type, so it fails to compile. `.optional()` plus a transform avoids it.

## 3. A `$` inside a secret in `.env` gets interpolated by Compose

Compose interpolates `$name` in env files. A generated value containing `$` — a `scrypt$N$r$p$salt$hash` string is the classic — arrives in the container with its fields replaced by empty variables. Login then fails with no error anywhere, and it works perfectly in tests because tests never go through Compose.

The tell is a warning you would otherwise ignore:

```
level=warning msg="The \"FlkOyTu\" variable is not set. Defaulting to a blank string."
```

Those "variable" names are fragments of your secret. Fix: choose a storage format Compose will not touch (base64 and `.` separators are safe), or escape as `$$`.

## 4. An unquoted value with a space cannot be `source`d

`NAME=Some Value` is fine for Compose and fatal for a shell:

```
./.env: line 12: Value: command not found
```

You find out when a script that sources `.env` silently loses that one variable. Quote it: `NAME="Some Value"`.

## 5. `docker compose down` while a hand-run container is attached orphans the network

```
! Network quivane-ops_default Resource is still in use
```

Compose refuses to remove a network that still has an endpoint, leaves the network behind, and exits 0 overall so it reads like success. Order matters: remove the container you started by hand (`docker rm -f <name>`) **first**, then `docker compose down`.

## 6. A Dockerfile's build context is not the Dockerfile's directory

A Dockerfile that copies several workspace packages needs the **repo root** as context. Pointing `build.context` at one package gives:

```
failed to compute cache key: "/packages/x/package.json": not found
```

Set `context: ..` and `dockerfile: packages/x/Dockerfile`, and add a `.dockerignore` so `node_modules` and build output are not sent.

## 7. Adding a cross-package import without rebuilding the image serves stale code

The build fails once the service imports a new workspace package the Dockerfile does not copy, so the image is not replaced — and the **old container keeps running**. Tests pass, the repo is correct, and the deployed thing behaves like the previous commit.

Whenever a service starts importing another package: update the Dockerfile to copy, install and build it in dependency order, then confirm the running container actually changed (a migration count, a version endpoint, a startup log line). "The tests pass" is not evidence that anything was deployed.

## 8. One env var doing two jobs

A var used as both the *published host port* and the process's *listen port* desynchronises the moment anyone changes it: the mapping points at 8080 and the process listens on the new value. Symptom: connection refused, config looks right.

Keep the internal port fixed in the container and expose a separate host-side var. When the published port is configurable, the public URL var (`SERVER_URL` and friends) must move with it.

## 9. Native addons on Linux: no prebuild, and Python 3.14 has no `distutils`

`node-pty` ships prebuilds for macOS and Windows only, so Linux compiles from source. That needs `gcc-c++` and `make`, and then `node-gyp@9` dies at **configure**:

```
ModuleNotFoundError: No module named 'distutils'
```

Python 3.13+ removed `distutils`, so install `python3-setuptools` for the shim **or** use a newer `node-gyp` (10+ does not import it). If you use `@electron/rebuild`, know that it refuses any path containing a space:

```
⨯ Attempting to build a module with a space in the path
```

Drive `node-gyp` directly instead — it does not care about the space:

```bash
npx node-gyp@11 rebuild --directory=node_modules/node-pty \
  --target=<electron-version> --dist-url=https://electronjs.org/headers --arch=x64
```

## 10. `localhost` is not `127.0.0.1` when only IPv4 is published

A container publishes on IPv4. `localhost` resolves to `::1` first, and a client that does not fall back (many Node HTTP clients do not) gets `ECONNREFUSED` while `curl` works fine because curl tries both.

Symptom: "Cannot connect to server" from a CLI, immediately followed by an *authentication* error, while the server is demonstrably up. Use `127.0.0.1` in configured URLs on any host where the service is reachable over IPv6 too.

See also: [[Skills/devops|devops]] · [[Skills/verify-by-running-it|verify-by-running-it]]
