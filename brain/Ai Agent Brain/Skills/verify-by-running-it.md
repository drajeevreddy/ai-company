# Verify by running it

The defect class that survives every unit test: code that is correct in-process and wrong once it is packaged, deployed, reconnected, or driven by a real client. Every item below passed a green test suite on the way to failing in reality.

The rule that catches them: **a phase is done when its command output exists, not when the code looks right.** Paste the response body, the row count, the log line. "The command exited 0" is not evidence.

## Defects that only appeared when it ran

- A strict schema over `process.env` — crash-looped on boot in a container only. [[container-env-and-secret-gotchas|See #1]].
- A `$` inside a generated secret — mangled by Compose on the way into the container, so a login that works in tests always failed. [[container-env-and-secret-gotchas|See #3]].
- An `unref()`'d **reconnect** timer. Socket closes, event loop drains, process exits 0 — so restarting the server silently killed every client, and it looked like a clean shutdown. Guard timers unref; the one that keeps you alive must not.
- A frame the server never sent. The server marked the task dispatched, the client waited forever, and nothing errored. Two independently-passing sides, one broken conversation.
- An audit row written only when a recipient happened to be connected over one transport, so the other transport left no trail.
- A Docker image that was not rebuilt after a new cross-package import. The container kept serving the **previous** commit while every test passed. [[container-env-and-secret-gotchas|See #7]].
- Real host port conflicts (`3000` and `8080` already taken), which is a config change only visible on a machine that is not yours.
- Two real clients on one machine, exchanging a message — the only way to prove a scoping rule refuses the case it is supposed to refuse.

## Techniques that paid for themselves

**Probe the smallest thing first.** When a client hangs, send one raw request with `curl` or `fetch` before suspecting the client. That single check separated "the endpoint is broken" from "the client is broken" in about a minute, after an hour of guessing.

**Drive the real protocol with the real library.** A real client against a real server over the real transport is what found the MCP calling-convention and stateless-mode defects. A handler unit test cannot see either.

**Wrap every network call in a timeout.** A hang reports nothing at all — worse than a failure, because there is no signal to follow. `Promise.race` with a named timeout turns a stall into a line you can read.

**Run the real container, not a local `tsx` run.** Most of the env, secret and build-context class above cannot reproduce outside the image.

**Verify a GUI on a headless box.** A display is not required, and "no display server" is not an excuse for claiming it is unverifiable:

```bash
sudo dnf install -y xorg-x11-server-Xvfb ImageMagick
Xvfb :99 -screen 0 1400x920x24 &
DISPLAY=:99 npx electron . --no-sandbox &
sleep 12
DISPLAY=:99 import -window root /tmp/shot.png     # ImageMagick, no xwd needed
```

Then actually look at the image. A first-run screen with a real error banner ("could not read <token path>: ENOENT") is worth more than any amount of reasoning about whether it would render. Kill the Xvfb process afterwards.

**Prove a native addon by using it.** After a native module compiles, spawn something real and assert the output and exit code — do not stop at "it built".

**When a shared fixture gains a table, update its truncate list.** A test harness that truncates a fixed set of tables let rows accumulate across runs, and an inbox assertion read three messages instead of one. Silent, order-dependent, and passing on a fresh database.

## Working with subagents

- **Freeze the contracts first**, then hand out work. Agents that share an interface definition drift; agents that share a written contract do not.
- **Disjoint file ownership, and one owner per shared file.** Parallel agents editing the same entry point will collide. Give exactly one of them the wiring line and have the other deliver a snippet.
- **Say what a phase must prove, and how.** "All tests pass" invites a green suite over an unverified path.
- **Explicitly ask for what could not be verified, and why.** Told to be honest, agents report it well — including the reason (missing toolchain, no display, no credentials). That is the most valuable part of their report.
- **Then verify the claim yourself.** Re-run at least one of their commands. A report is a claim; the output is the evidence.
- **Diff a child's findings against the report item by item.** Reading their file once is not reconciling it. A genuine MEDIUM (two entry points claiming the same row under different cache keys) was read but never itemised, because it sat under higher-severity items while skimming — diff by count and by topic, not by memory. And re-examine severities a child sets *higher* than yours: one rated a confirmed double-billing HIGH where the report said MEDIUM, and was right.
- **Re-probe anything a child says about live behaviour.** One asserted a build file was "publicly readable at `/_headers`"; a live probe showed the SPA rewrite answering with the shell, so it was source hygiene, not exposure. Children are reliable on source and drift on what is actually running. See [[Skills/audit-false-positives|audit-false-positives]].

See also: [[Skills/software-development|software-development]] · [[Skills/container-env-and-secret-gotchas|container-env-and-secret-gotchas]] · [[System/Astra-Operating-System|Astra-Operating-System]]
