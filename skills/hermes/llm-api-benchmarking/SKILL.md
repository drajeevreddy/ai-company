---
name: llm-api-benchmarking
description: Measure LLM API TPS/TTFT; use when asked to 'test the tps'.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [benchmarking, llm, openrouter, performance, tps]
---

# LLM API Benchmarking

Measure real streaming throughput (tokens/sec), time-to-first-token (TTFT), and end-to-end latency against any OpenAI-compatible chat completions endpoint.

## Quick start

Run the bundled benchmark script (defaults to the Hermes-configured model via OpenRouter):

```bash
python3 <skill_dir>/scripts/tps_bench.py
```

It reads `OPENROUTER_API_KEY` from `~/.hermes/.env` (never prints it), streams 4 completions, and reports per-run TTFT / total time / completion tokens / TPS plus a median summary.

To target another endpoint or model, edit the `MODEL` / `URL` constants or import `run_once` from the script.

## Method (why it is built this way)

1. **Stream with `stream_options: {"include_usage": true}`** so the final SSE chunk carries real `usage.completion_tokens` — chunk counts are only a fallback (~1 token/chunk is approximate).
2. **TTFT** = time of first non-empty `delta.content`, subtracted from total wall time to get generation time.
3. **Multiple runs (N=4)** and report median — single runs swing wildly.

## Pitfalls (all observed in real runs)

- **Buffer-flush bursts**: some responses arrive as one large flush after a pause. Generation time ≈ 0 produces absurd numbers (one run reported 719,389 tok/s). The script excludes runs where `gen_time < 0.5s` — never report these as real TPS.
- **Reasoning models can emit zero visible content**: a run may consume the full `max_tokens` on hidden reasoning (`completion_tokens=1200, streamed_chunks=0`). Guard: require `chunks > 5` before computing TPS, and raise `max_tokens` (1200+) so visible generation dominates.
- **End-to-end vs decode rate**: for user-perceived speed, also compute `completion_tokens / total_wall_time` (~60 tok/s for stealth/ox-alpha via OpenRouter, Aug 2026) — TTFT includes hidden reasoning time and can reach 25s.
- **Key hygiene**: load keys from `~/.hermes/.env` inside the script; never echo them to terminal output.

## Related but distinct

- gstack `benchmark-models` compares model QUALITY/cost side-by-side via prompts — not raw streaming throughput. Use that for "which model is best"; use this for "how fast is X".
