# Delegated research for a spec pack

The fact layer of a pack — framework behaviour, CLI surface, licence terms, component sourcing — is faster and cheaper to gather with parallel subagents than in the parent context. This is the shape that worked.

## Dispatch

Fan out 2–4 children, each bounded to one topic. Every goal must include:

- **The exact deliverable**: a compact fact sheet, organised by heading, with a length cap.
- **The source preference**: primary docs, raw repo files, npm/registry metadata, official API endpoints. Explicitly forbid drawing on model memory.
- **A per-claim URL requirement.** Every claim carries the URL it came from.
- **"Mark anything unconfirmed as UNVERIFIED"**, without hedging it into prose.
- **The constraint the reader cares about**, so the child answers the question the pack actually needs (for example: "we may not import AGPL-licensed packages", "the audience is an agent that will run install commands").

Use an output schema of `{ markdown: string, unverified_items: string[] }`. It forces the split between facts and gaps, and the gaps list is often the most valuable part of the return.

## Verify before you write

Child summaries are self-reports, not verified facts. Before a claim enters the pack, spot-check the load-bearing ones yourself with cheap primary fetches:

- `curl -s` on a raw file URL (`raw.githubusercontent.com/<org>/<repo>/<branch>/<path>`) and grep it.
- `curl -s` on the docs page's `.md` twin, or the site's `llms.txt` index, and grep for the exact claim.
- `curl -s -o /dev/null -w '%{http_code}'` on an endpoint whose auth behaviour is the claim.
- The platform API (`api.github.com/repos/<org>/<repo>`) for licence, branch and metadata fields.

Claims about a sandbox's limits, a precedence rule, or an auth gate are the ones that reshape a plan; verify those directly even when the child cites a URL.

## Un-truncating a child's summary

Long child summaries come back truncated in the parent context, with the full text saved to a cache path. The saved file is the JSON blob with an **escaped** `markdown` field, so line-based reading is useless until it is unescaped. Recipe:

1. Read the file, find the `"markdown": "` marker, take everything after it.
2. Cut at `"unverified_items"` and strip the trailing quote/comma.
3. Unescape in the right order — double-escaped sequences before single-escaped ones: `\\n` → newline, then `\n` → newline, then `\\"` → quote, then `\"` → quote.
4. Write it to a scratch `.md`, then print every line starting with `#` to get a section map.
5. Read only the line ranges you need. A 60 KB fact sheet usually has 3–4 sections that matter for the file you are writing.

## Reporting the fact layer

- Distil into `references/<topic>.md` under the pack, keeping each claim's URL and a short UNVERIFIED section at the end.
- Carry version pins as facts, not as truth: a package version is a snapshot and must be re-checked before a build pins it.
- When a later build contradicts a reference file, fix the reference file first, then the code — otherwise the next session trusts the stale fact again.
