# Multi-Agent Orchestration Pricing Snapshot — August 2026

Captured from live sources (traycer.ai docs, GitHub repo READMEs, vendor pricing pages) during a user consultation on 2026-08-21. Re-verify before relying on any number.

## Traycer Desktop (traycer.ai)

Pricing separates product access from inference usage.

| Plan | Price | Includes |
|---|---|---|
| **BYOA** | $0 | Local-only Traycer with your own coding agents (Claude Code, Codex, OpenCode, Cursor). No cloud sync, sharing, or Traycer credits. |
| Sync | $10/user/mo | Cloud sync, device switch, team collaboration. No inference credits. 7-day trial. |
| Lite | $20/user/mo | Everything in Sync + $20 monthly inference credits + bonus. |
| Pro | $40/user/mo | Everything in Lite + $50 credits + bonus. |
| Ultra | $100/user/mo | Everything in Pro + $150 credits + bonus. |

Credit mechanics:
- Credits apply ONLY to models accessed through the Traycer provider: upstream API price + **20% Traycer markup**. Credits do not roll over.
- Driving Claude Code / Codex / OpenCode / Cursor through BYOA consumes NO Traycer credits and adds no markup — those run on their own accounts/subscriptions.
- Key doc pages: `docs.traycer.ai/account/pricing`, `docs.traycer.ai/concepts/agent-to-agent` (agent-selection instructions let agents delegate to the right agent/model/reasoning effort).

## Vibe Kanban (BloopAI/vibe-kanban)

- Free, open source; run with `npx vibe-kanban`.
- Supports 10+ agents: Claude Code, Codex, Gemini CLI, GitHub Copilot, Amp, Cursor, OpenCode, Droid, CCR, Qwen Code.
- Kanban issues → workspaces (each = git worktree + branch + terminal + dev server), diff review with inline comments back to the agent, built-in preview browser, PR creation/merge.
- **STATUS: SUNSETTING** — README banner links to vibekanban.com/blog/shutdown. Still functional and self-hostable (Docker guide exists) but development frozen. Treat as maintenance-mode software.

## GitHub Agent HQ

- Announced Feb 4, 2026. Claude (Anthropic) and OpenAI Codex available in public preview alongside Copilot on GitHub, VS Code, GitHub Mobile.
- Requires Copilot Pro+ ($39/mo individual) or Copilot Enterprise.
- Copilot Pro ($10/mo) does NOT unlock third-party agents in HQ.

## Hermes-native (no new software)

- `hermes chat -q '<task>'` — one-shot worker, no PTY needed.
- tmux sessions for interactive parallel agents (`tmux new-session -d -s name 'hermes -w'`).
- `-w` worktree mode prevents edit collisions between parallel file-editing agents.
- `delegate_task` tool for quick parallel subtasks inside a session.

## Decision heuristic for this user

User already pays subscriptions for claude-code/codex/opencode → orchestration layer should be free: Traycer BYOA (desktop, agent-to-agent loops) or Hermes-native (terminal). Vibe Kanban only if open-source web UI is preferred and frozen dev is acceptable. Agent HQ only if GitHub-native mobile/cloud dispatch is wanted — it duplicates existing capability at $39/mo.
