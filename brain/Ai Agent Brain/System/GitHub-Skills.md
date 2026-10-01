# GitHub Skills (installed 2026-09-12)

Real skills pulled from GitHub via `hermes skills install` (security-scanned). All show `enabled`.

## Design — award-winning bar
- `frontend-design` (creative, anthropics/skills) — distinctive visual identity, opinionated palette/type/layout, never templated defaults. Load for every new UI.
- `web-design-guidelines` (creative, vercel-labs/agent-skills) — Vercel's Web Interface Guidelines compliance review: accessibility, UX audit.
- `canvas-design` (creative, anthropics/skills) — static art/posters via design philosophy → canvas.
- `theme-factory` (creative, anthropics/skills) — 10 preset themes + on-the-fly theme generation for artifacts/slides/pages.

## Code — quality bar
- `vercel-react-best-practices` (software-development, vercel-labs) — 70 React/Next.js perf rules across 8 categories. Load when writing, reviewing, or refactoring React.
- `vercel-composition-patterns` (software-development, vercel-labs) — compound components, boolean-prop cleanup, reusable APIs, React 19 changes.
- `webapp-testing` (software-development, anthropics/skills) — Playwright testing via `scripts/with_server.py` (run `--help` first, treat scripts as black boxes).

## Meta
- `skill-creator` (software-development, anthropics/skills) — write/improve/eval skills. Install needed `--force`: scanner flagged the word "exfiltration" in a sentence forbidding it (false positive, verified by reading line 113).

## Skipped deliberately
- `brand-guidelines` (Anthropic-only branding), `web-artifacts-builder` (claude.ai artifact pipeline), `blader/humanizer` + `conorbronsdon/avoid-ai-writing` (our local `humanizer` port is fuller).
- Already had equivalents: docx/pdf/pptx/xlsx.

## Quality loop (use together)
1. Design: `frontend-design` for direction → build → `web-design-guidelines` + [[Award-Winning-Design]] to audit.
2. Code: `vercel-react-best-practices` + `vercel-composition-patterns` while writing → [[Code-Quality-Bar]] 10/10 check.
3. Prose: [[Anti-Slop-Prose]] P0/P1/P2 pass.
4. Interactivity: `webapp-testing` to prove it works.

## Token saving (installed 2026-09-12, `mocasus/paleo` pack — all scanned clean)
- Already had: `caveman` (ultra-compressed, ~65% fewer tokens), `ponytail` (laziest working solution), `freeze`/`context-save`/`context-restore`.
- `paleo` — terse replies, ~50-70% fewer output tokens, code/commands byte-exact. Trigger: "paleo mode".
- `paleo-auto` — auto-enables the pack on long sessions/high usage. Trigger: automatic past ~15 turns.
- `paleo-budget` — hard per-task token caps. Trigger: "stay under N tokens".
- `paleo-converse` — condense history, keep last N turns verbatim. Trigger: "condense chat".
- `paleo-json` — minified structured output. Trigger: "compact json".
- `paleo-summary` — condense bulky tool output/logs/diffs. Trigger: "tldr".
- `paleo-trim-context` — proactively drop stale context, keep task state.
- Note: every installed skill adds ~40 tokens/turn to the skill index — the pack pays for itself only when used. Disable idle ones via `hermes skills config`.
- Laziness doctrine: [[Ponytail]] — the ladder, YAGNI, shortest-diff-wins.

 doctrine: [[Astra-Operating-System]] · sources: [[Sources]]
