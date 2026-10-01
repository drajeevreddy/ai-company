# webcmd Knowledge Bank

Condensed from research on 2026-08-06 for the SLAB hackathon (Christ University, Bangalore — 22 Aug 2026). Full battle plan lives at `~/Desktop/SLAB-HACKATHON-PLAN.md`.

## Authoritative links

| Resource | URL |
|---|---|
| GitHub repo | https://github.com/agentrhq/webcmd |
| Agent setup guide (start.md) | https://raw.githubusercontent.com/agentrhq/webcmd/main/start.md |
| Docs home | https://webcmd.dev/docs |
| Prompt cookbook | https://webcmd.dev/docs/agent-prompts |
| Concepts (how it works) | https://webcmd.dev/docs/concepts |
| CLI reference | https://webcmd.dev/docs/cli-reference |
| X→CLI learning pattern | https://webcmd.dev/docs/x-session-cli |
| Publish community plugin | https://webcmd.dev/docs/publish-community-plugin |
| npm package | https://www.npmjs.com/package/@agentrhq/webcmd |
| Prior SLAB winner-style project | https://github.com/ArchitBhattacharya/slab-project |

## What webcmd replaces / overrides

Per start.md: webcmd suggests disabling harness webfetch + browser-navigation tools because it is fully local (no 3rd-party fetch services), cheaper via smarter snapshots, and has stealth mode for better access. When both are available, prefer webcmd for page fetches and browser work.

## Plugin catalog (as of 2026-08)

Community plugins: `omnisearch` (no-login research across HN, Stack Overflow, GitHub, arXiv, Dev.to, Lobsters, Bluesky), `pypi` (package metadata), `skyscanner` (flight search). Built-in supported surfaces include: Hacker News, Reddit, PubMed, X/Twitter, LinkedIn, TikTok, ChatGPT, Claude, Gemini, NotebookLM, Amazon, Blinkit, Zepto, BigBasket, District, Practo. Search before assuming: `webcmd plugin search <site> -f json`.

## SLAB hackathon judging (100 pts)

- Live reliability: 30
- Real-world usefulness: 25
- Technical depth & recovery: 20
- Creativity: 15
- Demo quality: 10

Theme: "Build an agent that solves a meaningful, real-world browser workflow." Any stack allowed (Codex, Claude Code, OpenClaw, Playwright, Browser Use, browser MCPs, local/hosted models). webcmd team on-site for setup/debugging.

## SlotSniper (our entry) — one-paragraph summary

Self-healing appointment concierge: hunts earliest endocrinology OPD slots (Practo discovery + our own Dizi Doc portal at localhost:8080 as the controllable booking target), books the chosen slot, notifies the patient on Telegram. Signature demo beat: flip a feature flag on our own site to break the compiled adapter live on stage → agent detects failure → re-explores (Layer 0) → recompiles adapter (Layer 2) → completes booking anyway. Hits reliability + recovery + creativity in one sequence. Full phased build plan, demo script, risk table, master build prompt, and Mission Control UI spec: `~/Desktop/SLAB-HACKATHON-PLAN.md`.

## Differentiation lesson (from prior SLAB Kolkata)

The "search → open each result → LLM-extract JSON → filter noise → rank" pattern (internship hunter) already exists. Judges saw it. Differentiate with the self-healing/learning loop, controlled-site live-break demo, or domain-specific usefulness — not another scrape-and-rank.
