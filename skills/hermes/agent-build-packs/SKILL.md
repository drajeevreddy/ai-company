---
name: agent-build-packs
description: "Author agent build packs: prompt, contracts, briefs."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Agent Instructions, Spec Authoring, Delegation, Contracts, AGENTS.md]
    related_skills: []
    editorial_name: Agent Build Packs
    editorial_description: Turn a product brief into the instruction layer coding agents execute.
    requires_tools: [read_file, write_file, patch, terminal, delegate_task, execute_code]
---

# Agent build packs

## When this applies

The user hands over a product brief as prose (often a long "master prompt" they drafted) and wants it turned into something coding agents can execute. The deliverable is a folder of markdown — a prompt pack — not code. Also applies when they say "make this prompt better" or "add agent files".

The pack is read by two audiences at once: an agent that must execute without guessing, and a human who must review what was decided. Write for both.

## Deliverable shape

Keep this structure; add files freely, but do not rename these six roles away.

| File | Carries |
|---|---|
| `MASTER-PROMPT.md` | The build brief: mission, MVP as one concrete end-to-end flow, architecture with per-service responsibilities, hard constraints, deliverables per path, UI, security model, phases, non-goals, open questions, working agreement |
| `AGENTS.md` | Standing rules for any agent in the repo: hard constraints with the exact check commands, architecture invariants, engineering rules, verification bar, definition of done |
| `contracts/<interface>.md` | One file per interface between components: wire protocol, HTTP API, data model, policy tables |
| `agents/<NN>-<component>.md` | One brief per component, plus an orchestrator and a reviewer |
| `references/<topic>.md` | External facts, each with the URL it came from |
| `README.md` | Index, how to use the pack, verified-vs-unverified status |

Two derived artifacts make the pack usable by a human rather than only by an agent, and they are
cheap once the sources exist:

| Derived file | Why |
|---|---|
| `<SLUG>-BUILD-PACK.md` | Every file concatenated in reading order with a numbered contents list. Somebody will want one document to read or forward; generate it from the source files **after** they are final, never by hand, so it cannot drift. Mark the concatenated copy non-authoritative in its header and point at the individual files. |
| The rewritten plan document | When the input was the user's own spec, return a clean top-level version of it with the deltas already applied. That is usually what they actually asked for, and it is the artifact they will show other people. |

**Handover format.** Deliver markdown files in a folder, name the absolute path, and zip only when
asked. Do not produce a PDF unless the user asks for one by name — in a terminal session the
attachment channel is not intercepted, so a PDF path is just a longer string, while the markdown is
immediately editable by whoever receives it.

## Procedure

1. **Fix the constraints before writing prose.** Verify the host platform's real behaviour from its own docs (many doc sites expose `.md` twins of every page, or an `llms.txt` index; monorepos expose raw file URLs). Verify the licence/terms surface of anything the build will depend on. Anything you cannot confirm becomes an explicit UNVERIFIED line in the pack — never smoothed into confident prose.

2. **Freeze the interfaces next, before any component brief.** A protocol left implicit is where parallel agents drift. Every contract states: transport and auth, the message/field envelope, the full state machine with who owns each transition, idempotency keys, failure and retry behaviour, rate or volume caps, and the names reserved for features that are explicitly not built yet.

3. **Make policy deterministic.** "A configurable risk threshold" is not a spec. Write a scored table with machine-named reasons, the threshold, the override conditions, and the gate end to end (who decides, what is stored where, what happens on expiry, what the audit record says). Numbers and reason keys, not adjectives.

4. **Write the master prompt with the delta visible.** When improving a prompt the user already wrote, open with a short "what changed and why" section naming the gaps you closed. They asked for better, and they will check that you improved rather than rewrote.

5. **One role brief per component.** Each brief states: files owned, inputs (which contracts and reference files), required output, acceptance commands, and anti-goals. Include an orchestrator brief that fixes phase order, a verification-before-next-phase rule, and stop conditions; include a reviewer brief whose first blocking check is the licence constraint.

6. **Phases close on command output, not opinion.** Every phase names the commands that prove it and where the output is pasted. A phase that cannot be verified by a command is a phase that will be declared done on vibes.

7. **Close the cross-reference set, then verify it.** Every path referenced in backticks falls into
   one of two sets, and they need different checks:

   - **Pack-internal** (paths under the pack's own directories, plus the six top-level files) — must
     resolve to a file that exists. An unresolved one is a defect.
   - **Build outputs** (`src/`, `tests/`, `scripts/`, and anything the pack tells an agent to create)
     — must each appear somewhere in the master prompt's deliverables tree. A referenced output that
     the master prompt never declares is a spec gap an agent will fill by guessing.

   Script the check rather than eyeballing the pack; it is a regex over backticked tokens, then a
   set-difference per side. Report both numbers — `0 unresolved, 0 undeclared outputs` — because a
   check with no output is indistinguishable from a check that never ran.

## Always-on rules

- **Concrete over principled.** When the user asks for "UI details" or "how to pull components", they want install commands, registry handles, package names, auth requirements and cost caps — not "use a component library". Name the source, the command, the licence and the catch.
- **State the cost and gate of every paid or authenticated source.** Free tier, auth requirement, per-day caps, membership walls. A source that silently needs an account is a blocker discovered mid-build.
- **Do not restate what the environment already teaches.** Tool schemas, the repo's own AGENTS.md, a framework's getting-started page — the pack carries decisions the environment cannot know, not a copy of it.
- **Mark unverifiable claims.** Which React version a host provides at runtime, the internal shape of a generated manifest, whether a capability sits behind a paid tier: say UNVERIFIED and say what would settle it. A wrong confident claim in a spec costs a day.
- **Point at primary sources, not at your summary of them.** Reference files carry URLs next to claims so a later session re-verifies instead of trusting the file.
- **Keep the master prompt paste-able.** An agent should be able to take `MASTER-PROMPT.md` plus one role brief and start working. Anything that requires reading all six files before the first commit belongs in the orchestrator brief instead.
- **Voice.** Plain imperatives, no hype, no restating the user's request back at them, no filler openers. A pack full of "leverage" and "robust" trains the agents that read it to write the same way.
- **Name what is deliberately not built**, with the extension point reserved in a contract, so the MVP stays tight and the future path is not a redesign.

## Verification before reporting done

- Grep every backticked path; unresolved references are a defect.
- Confirm no forbidden dependency appears in any install line you wrote into the pack (grep the pack for `add`/`install` lines against the blocked list).
- Report the file count and size, and state plainly which claims are verified and which are UNVERIFIED.

## Support files

- `references/agent-context-files.md` — which instruction files an agent host auto-loads, precedence between them, the protected-name approval gate, and how to wire an external doctrine vault into every session.
- `references/delegated-research.md` — running parallel research subagents for the fact layer, un-truncating their summaries, and spot-checking load-bearing claims yourself.
- `references/replit-host-facts.md` — Replit as a host: app-scoped `DATABASE_URL` (which rules out a second service), deployment types and the one that silently breaks schedulers, the two-database dev/prod split, and no managed Redis.
- `references/prompt-layer-patterns.md` — when the pack contains an AI feature: the five prompt artifacts, structural variation axes, the critique pass, the three-layer eval harness, and what the AI contract must pin down.
