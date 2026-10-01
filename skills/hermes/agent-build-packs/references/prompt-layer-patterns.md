# Prompt layers for AI features in a build pack

When a pack includes an AI feature and the user says "fix the prompting", the deliverable is not a
rewritten prompt. It is a layer of five artifacts, and the code contract that binds them. A single
"write me three captions" prompt returns three paraphrases of one sentence, and no amount of wording
fixes that — the fix is structural.

## The five artifacts

| File | Role | Call count |
|---|---|---|
| `prompts/<feature>-system.md` | Generation. Role, hard rules, voice, platform craft, self-check, output shape | once per set |
| `prompts/<feature>-axes.md` | The variation matrix and the exact user message that selects one combination per variant | merged into the user message |
| `prompts/<feature>-guard.md` | A separate low-temperature critique pass that scores, lists issues by machine-named code, and *repairs* | once per set, sees all variants together |
| `prompts/<feature>-eval.md` | Golden briefs, deterministic assertions, LLM-judge thresholds | CI |
| `contracts/ai-<feature>.md` | Input schema, output schema, limits, cost, caps, failure modes | the contract the prompts fulfil |

Version each prompt with a `# version:` header comment and record that version on every run row, or
you cannot attribute a quality change to a prompt change.

## Variation must be structural, not lexical

Define two or three orthogonal axes and assign each variant a fixed combination, so the set is
reproducible and testable:

- **hook type** — question, stat, contrarian, story, instruction, observation
- **proof type** — none, number, named-example, comparison, direct-experience
- **close type** — none, soft, direct, link, referral

Two variants sharing a hook are the same variant wearing different clothes. Make that a *machine
check* ("the three `hookType` values are pairwise different"), not a hope. The axes file states the
matrix; a pure function in code selects the combination from the brief and is unit tested.

## The critique pass is where the quality comes from

- Temperature near zero. A guard that varies is not a guard.
- It sees all variants in one call, because the most common defect is siblings that repeat each other.
- It **repairs** rather than rewrites: swap a banned word, move the hook above the truncation fold,
  split the run-on, delete an unsupported claim, append the missing close.
- Issue codes are a closed set (`banned-word`, `claim-unverified`, `hook-buried`, `rhythm-flat`,
  `duplicate-of-sibling`, …). Free-text critiques cannot be asserted on or counted.
- Every variant carries a verdict (`pass` / `revised` / `rejected`), so the user sees *why* something
  was rejected instead of an empty result. Never return nothing; return the best variant flagged.

## The eval harness is what stops the drift

Three layers, in `pnpm test:prompts`:

1. **Deterministic, no model** — banned-word regex over a union list, character limits counted on the
   real string (never trust the model's own count), required axes present, no invented numerals,
   sentence-length variance above a floor, no two consecutive long sentences, JSON parses without the
   repair retry. A repair-retry rate above ~10% means the output-schema instructions are unclear and
   every extra round trip is billed to a user.
2. **Judge with thresholds** — a second model scores named dimensions with the rubric inline, and the
   build fails below a mean. One dimension is absolute: an invented claim fails the build at a rate
   above zero.
3. **Agreement report** — print where the guard passed something the judge scored badly (a missing
   check) and where the guard rejected something the judge liked (an over-firing trigger). That list,
   not the pass rate, tells you which prompt to edit.

Golden briefs are unpleasant on purpose: no-number briefs (to catch invented statistics), adversarial
briefs ("write a viral hook"), reference-copy briefs, and one real sanitised production brief. A new
failure mode discovered in production becomes a new brief **before** the fix. Never loosen a threshold
to make a run pass — that converts a measurement into a vibe.

## What the contract must pin down

- Platform character limits, counted server-side after generation, and trimmed at a clause boundary.
- Cold-start output budget and a ledger row per call (tokens, model, latency, cost, cache hit) written
  **before** the response returns, including failures.
- Caps enforced from the ledger before the call, never from a counter. At cap, refuse with a reset
  date rather than making a call you cannot bill.
- A deterministic cache key over the brief plus the prompt version, so repeated demo clicks cost
  nothing and the hit ratio is visible.
- A provider-agnostic gateway (OpenAI-compatible HTTP, timeout with `AbortController`, one primary and
  one fallback, record which provider served). No vendor SDK, so the provider is a config change.
- Never send customer records — contact emails, deal values, invoice amounts — into a prompt. The
  feature gets the brief and nothing else.

## Anti-slop rules belong in the prompt, verbatim

Put the banned vocabulary and the banned *structures* in the system prompt as a list the model reads,
not only in the pack's style guide. Structures matter more than words: "it's not X, it's Y", a
rhetorical question answered in the next line, a rule-of-three list standing in for an argument, an
`-ing` clause bolted on for depth. If the user's product generates text a human reads, this list is
a product feature and belongs in the eval set as assertions.
