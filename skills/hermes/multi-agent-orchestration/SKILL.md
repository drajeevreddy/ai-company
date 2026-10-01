---
name: multi-agent-orchestration
description: Orchestrate many coding CLI agents; use for agent teamwork.
version: 1.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [orchestration, multi-agent, claude-code, codex, opencode, vibe-kanban, traycer]
---

# Multi-Agent Orchestration

The user runs many coding CLIs (claude-code, codex, opencode, cursor-agent, vibe, command-code, mimo, hermes). Recurring need: make 3+ parallel CLI agents share context and work together instead of isolated terminals.

## Tool landscape (verified Aug 2026 — re-verify pricing/status before acting)

| Tool | Cost | Model | Notes |
|---|---|---|---|
| **Traycer** (traycer.ai) | **$0 BYOA** / $10 Sync / $20-100 credit tiers | Desktop app | BYOA = local-only, drives user's own agents on user's own subscriptions, no Traycer markup. Native agent-to-agent delegation loops. Best fit for this user. |
| **Vibe Kanban** (`npx vibe-kanban`) | Free OSS | Local web kanban | **Sunsetting** (announced, repo banner). Still functional/self-hostable but frozen. Git-worktree isolation per task. |
| **GitHub Agent HQ** | Copilot Pro+ $39/mo | GitHub/VS Code/Mobile | Claude + Codex + Copilot on same tasks. Duplicates what user already has. |
| **Hermes-native** | Free | Terminal | Spawn CLIs via `hermes chat -q` (one-shot) or tmux sessions (interactive); `hermes -w` worktree mode prevents edit collisions; `delegate_task` for parallel subagents. Zero new software. |

Decision heuristic: user already pays for the underlying CLIs → recommend Traycer BYOA (free orchestration layer) or Hermes-native; skip Agent HQ.

## Hermes-native orchestration patterns

```bash
# One-shot worker (no PTY needed)
hermes chat -q 'Research X and write ~/research/x.md'

# Interactive parallel agents via tmux (prompt_toolkit needs a real terminal)
tmux new-session -d -s backend -x 120 -y 40 'hermes -w'
tmux send-keys -t backend 'Build REST API' Enter
tmux capture-pane -t backend -p | tail -30
```

- `-w` (worktree mode) for any agent that edits files — prevents git conflicts between parallel agents.
- Prefer `delegate_task` for quick subtasks; spawn full processes only for long autonomous missions.

## Review-gated agent pipelines

Use when several agents hand one deliverable down a chain (producer -> creative -> publisher) and a
human's rulings have to survive every hop.

- **Lock the human's rulings in one file that outranks every brief.** The reviewer's first act is to
  write the facts file (`<project>-brand-facts.md` or equivalent) holding the decided values, the
  banned list, and a sourced-claims section. Say in the file that it overrides all other briefs and
  that anything disagreeing with it is wrong. Without it, rulings drift back to the original brief by
  the third hop.
- **Record pending rulings as blocking, not as open questions.** "No design output ships until this
  is ruled" keeps a whole pipeline honest; a paragraph of open questions gets worked around.
- **Only sourceable claims ship.** Rule: a number or a named technology may appear only if traceable
  to a written source recorded *in the file*, with the source named. Retire contradicted claims
  outright rather than picking the more flattering set.
- **Verify the deliverable by extracting it, never by reading the producer's own checklist.** Peers
  file compliance summaries that overstate ("zero digits", "all versions within limit", "items 1/3/4
  untouched"), and a false summary costs a full independent re-verification every round. Recipe:
  `references/review-gating-agent-output.md`.
- **Before reissuing a review, string-match each instruction against the artifact.** A producer can
  file a complete new version that ignores the review in front of it because it is still working from
  a superseded brief. Confirm which items landed, name the ones that did not, and ask for a receipt
  (quote the request id) instead of re-explaining.
- **Name what must NOT change, not only what must.** "Revise items 2 and 5 in place, leave 1 and 4
  exactly as they are" is what stops a producer rewriting work you already approved.
- **When free-form instruction fails on the same item twice, send exact replacement strings.** Quote
  the current line and the replacement. It converges faster than a third round of prose.
- **Never serialise the pipeline behind one blocked item.** Hand the approved items downstream and
  hold only the blocked one; instruct the producer to do both in the same turn.
- **Every ruling found during review goes into the facts file, not just into the next message.**
  Otherwise the same defect returns the moment a new producer joins the chain.
- **Correct your own files when a producer's flag beats you.** Recount the source yourself; if the
  producer is right, fix the facts file and credit the correction in it so it is not re-litigated.
- **A canvas peer cannot see your terminal.** Any constraint that lives only in your transcript does
  not exist for the peer: put it in the message, or in a file on disk and name the path in the message.
- **Message only what you are wired to.** On a chained canvas you can reach your direct neighbour, not
  the whole team, so a task for a downstream agent travels as a relay instruction inside the message
  you send your neighbour. Read the canvas node/connection list before routing.
- **A queued message is not a delivered one.** Send once and never retry on silence; keep the request
  id so you can establish later whether it ever arrived. Check a peer's busy/idle status before
  sending work that depends on a report it may still be writing.

## References

- `references/review-gating-agent-output.md` — the extraction pass for verifying an agent-produced
  deliverable against hard constraints (limits, banned terms, placeholders, empty slots, claim
  classification).
- `references/pricing-snapshot-2026-08.md` — detailed pricing/feature comparison captured this session (Traycer tiers, credit mechanics, Vibe Kanban sunset).

## Related

- gstack `pair-agent` — pairs a REMOTE agent with the user's browser (different problem).
- `hermes-agent` skill — spawning/orchestration quick-start (protected; do not edit).
