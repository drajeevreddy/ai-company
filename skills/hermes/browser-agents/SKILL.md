---
name: browser-agents
description: "Use when building browser agents with the webcmd CLI."
---

# Browser Agents (webcmd)

Class-level skill for building AI browser agents on **webcmd** (@agentrhq/webcmd) — self-learning browser infra that watches how agents navigate a site, then compiles that knowledge into deterministic CLI commands (cuts token spend up to 90%).

## Core mental model: the 4-layer learning ladder

| Layer | Scenario | Mechanism |
|---|---|---|
| 0. Live browser control | Site unfamiliar | `webcmd browser` — inspect, click, type, extract, capture network calls |
| 1. Sitemap memory | Site familiar-ish | Captured sitemap of observed pages, states, actions, APIs, pitfalls |
| 2. CLI authoring | Action space known | Reusable `webcmd <site>` adapter with structured JSON output |
| 3. Extend existing CLIs | Workflow deterministic | Workflow runs instantly, minimal tokens |

**Key design principle for agents:** always try cheap `webcmd web fetch` first; only spin up a full browser session when a site blocks plain fetches. LLM parses unstructured pages (strict JSON schema, prefer "return fewer results than wrong ones"), but compiled adapters remove the LLM from navigation entirely.

## Setup

```bash
webcmd --version                  # Node.js 20.6+ required
npm install -g @agentrhq/webcmd   # fresh install
webcmd update                     # updates (NEVER npm-update once installed)
webcmd doctor                     # MUST be green before browser commands work
webcmd skills add                 # installs webcmd-usage skill into the harness
webcmd plugin search <site> -f json
webcmd plugin install <source>
```

Agent bootstrap prompt (paste into any coding agent):
```
Fetch and follow https://raw.githubusercontent.com/agentrhq/webcmd/main/start.md to set up Webcmd end to end.
```

## Session pattern

Profiles are cookie jars; sessions are independent browser windows (parallel agents need separate sessions). Adapter commands use an adapter-default session unless `--session` overrides.

```bash
webcmd session create -f json
webcmd --session session_abc browser run --file explore.js
printf 'return await page.title();' | webcmd --session session_abc browser run --stdin
webcmd session close session_abc
```

## Architecture pattern: self-healing agent

The signature capability webcmd enables (and what wins demos/judges):
1. Agent completes workflow via compiled adapter (Layer 2)
2. Site UI changes → adapter fails (selector miss / 4xx)
3. Agent DETECTS the failure class → drops to Layer 0 re-explore → recompiles adapter → retries → succeeds

State machine: `IDLE→EXPLORE→COMPILE→HUNT→BOOK→NOTIFY`, with `HEAL` re-entering EXPLORE on failure. Emit every step as structured events (`{ts, layer, action, detail, status}`) over WebSocket so a dashboard can narrate the agent's brain live.

## Known ecosystem notes

- Existing community plugins: omnisearch (HN/SO/GitHub/arXiv multi-search), pypi, skyscanner. Supported surfaces include Practo, Blinkit, Zepto, LinkedIn, X — availability depends on installed plugins.
- Prior art: SLAB hackathon (webcmd-powered) winning-style project = "search → open → LLM-extract → filter → rank" internship hunter (github.com/ArchitBhattacharya/slab-project). That scrape-and-rank shape is now common — differentiate via the self-healing/learning loop, controlled-site live-break demo, or domain-specific usefulness — not another scrape-and-rank.
- Don't anchor a build/demo to a production-like app just because a research plan names it. Confirm the target world with the user FIRST (they may say "that's a completely different project") — prefer scaffolding a self-contained mutable world (own sites on their own ports) over borrowing an unrelated app. A controllable local world makes the chaos/heal demo deterministic anyway.
- Event streams being green ≠ UI being good. Before claiming any dashboard/UI works, LOOK at it: drive a headless session, take screenshots, review with vision. Users react badly to confident claims about interfaces never visually inspected ("the UI is bullshit — where is it working"). Iterate fix → screenshot → re-review until it passes a critical eye.
- Runtime gotchas for webcmd programs (escaping in evaluate bodies, artifact paths, networkidle vs SSE, Node-vs-page context, output caps, real-pharmacy scraping patterns) live in `references/webcmd-runtime-gotchas.md` — read it before generating browser-run programs or debugging one that failed.

## Support files

- `references/webcmd.md` — condensed knowledge bank: links (docs, cookbook, CLI reference, X→CLI pattern), plugin catalog notes, and hackathon-specific context (SLAB judging rubric, SlotSniper project plan location).

## Pitfalls

- Don't hand-write one-off scripts from memory when a webcmd-usage skill is installed — follow the skill guidance; close sessions when done.
- Sites with anti-bot walls (pharmacies, Practo) can block live demos — always have a controlled localhost target or pre-recorded fallback.
- `webcmd doctor` must pass before any browser command; fix only what it reports, don't proceed around it.
