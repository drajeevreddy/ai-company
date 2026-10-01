# Skills

Total: 333 skills across 19 areas. Load any skill with `skill_view(name)`.

See: [[Specialties]] for the opinionated shortlist, [[00-Agent-Brain-Index]] for the vault home.

## Areas

- [[Skills/ai-engineering.md|ai-engineering]] (1)
- [[Skills/autonomous-ai-agents.md|autonomous-ai-agents]] (129)
- [[Skills/creative.md|creative]] (45)
- [[Skills/data.md|data]] (1)
- [[Skills/devops.md|devops]] (9)
- [[Skills/email.md|email]] (2)
- [[Skills/github.md|github]] (5)
- [[Skills/gstack-core.md|gstack-core]] (68)
- [[Skills/media.md|media]] (4)
- [[Skills/mlops.md|mlops]] (7)
- [[Skills/mlops-inference.md|mlops-inference]] (1)
- [[Skills/note-taking.md|note-taking]] (1)
- [[Skills/productivity.md|productivity]] (18)
- [[Skills/research.md|research]] (7)
- [[Skills/security.md|security]] (4)
- [[Skills/smart-home.md|smart-home]] (1)
- [[Skills/social-media.md|social-media]] (3)
- [[Skills/software-development.md|software-development]] (25)
- [[Skills/web.md|web]] (2)

## Project-local skills (not in the mirrored catalog)

The areas above mirror skills installed in Hermes. A few skills live outside that
catalog — referenced by vault notes but never installed globally. Listed here so
their references resolve.

- **quivane-design-system** — loads [[Projects/Quivane-Design-System]]; the INSPO visual
  language (`#D30000` red on `#FEFEFE`, 4.2–4.6% outer margin, sans-only). Referenced by
  [[Projects/Quivane-Social]].
- **october-canvas-bus** — the October workspace canvas bus: `message_peer` reaches only
  directly-connected peers, so use `send_to_node` with a node id to reach Juno and Athena.
  Referenced by [[Projects/Quivane-Social]].

## Most-used

- [[Skills/security.md|security]] — pentest hunts, RLS audit, hardening
- [[Skills/software-development.md|software-development]] — debugging, TDD, review, Supabase fixes
- [[Skills/creative.md|creative]] — HyperFrames video, design, graphics
- [[Skills/autonomous-ai-agents.md|autonomous-ai-agents]] — coding CLIs, multi-agent orchestration
- [[Skills/devops.md|devops]] — Vercel, Supabase ops, deploy troubleshooting
- [[Skills/multi-tenant-rls-audit.md|multi-tenant-rls-audit]] — tenant-isolation review procedure; core lesson in [[Skills/a-role-is-not-a-tenant.md]]

## Lessons (distilled)

Notes written from real builds, not summaries. Read the relevant one before debugging in that area.

- [[Skills/container-env-and-secret-gotchas.md|container-env-and-secret-gotchas]] — strict schemas over `process.env`, `coerce.boolean`, `$` in a secret mangled by Compose, build context, stale images, port vars, native addons, `localhost` vs `127.0.0.1`
- [[Skills/verify-by-running-it.md|verify-by-running-it]] — the defect class that survives every unit test; probing the smallest thing first; headless GUI verification with Xvfb + ImageMagick; working with subagents
- [[Skills/audit-false-positives.md|audit-false-positives]] — how to delete half an audit: the SPA catch-all, secret-pattern substring matches, transparent-text contrast artefacts, ungated-function scanner artefacts; test both themes; reconcile subagent findings; scan by value before publishing
- [[Skills/mcp-server-gotchas.md|mcp-server-gotchas]] — MCP servers: the `inputSchema` calling convention, stateless Streamable HTTP, shared token verifiers, testing the protocol not a mock
- [[Skills/credential-and-authority-design.md|credential-and-authority-design]] — one credential one blast radius, 404-not-403 for other people's records, narrow sharing defaults, audit at the action, anything that creates work cannot approve it
- [[Skills/supabase-vercel-tooling-gotchas.md|supabase-vercel-tooling-gotchas]] — Supabase CLI + Vercel CLI traps
- [[Skills/rls-hardening-playbook.md|rls-hardening-playbook]] · [[Skills/rls-verification-harness.md|rls-verification-harness]] · [[Skills/a-role-is-not-a-tenant.md|a-role-is-not-a-tenant]] — Postgres RLS: fixing, proving, and the one that generalised
