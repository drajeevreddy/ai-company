#!/usr/bin/env python3
"""TPS benchmark for an OpenAI-compatible streaming endpoint (default: Hermes model via OpenRouter).

Reads OPENROUTER_API_KEY from ~/.hermes/.env (never prints it).
Streams N completions, reports TTFT / total / completion tokens / TPS per run + median.

Guards (learned the hard way):
- excludes buffer-flush bursts (gen_time < 0.5s) that produce absurd TPS
- excludes runs with <=5 streamed chunks (reasoning models can emit zero visible content)
"""
import json, time, statistics, urllib.request, os, sys

ENV = os.path.expanduser("~/.hermes/.env")
key = None
with open(ENV) as f:
    for line in f:
        if line.startswith("OPENROUTER_API_KEY="):
            key = line.strip().split("=", 1)[1]
            break
if not key:
    sys.exit("No OPENROUTER_API_KEY found in ~/.hermes/.env")

URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "stealth/ox-alpha"  # edit to target another model
PROMPT = ("Write a detailed 400-word essay about the history of maritime navigation, "
          "from celestial navigation to GPS. Be thorough and specific.")
N = 4
MAX_TOKENS = 1200  # high enough that visible generation dominates hidden reasoning


def run_once():
    body = json.dumps({
        "model": MODEL,
        "messages": [{"role": "user", "content": PROMPT}],
        "stream": True,
        "stream_options": {"include_usage": True},
        "max_tokens": MAX_TOKENS,
    }).encode()
    req = urllib.request.Request(URL, data=body, headers={
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    })
    t0 = time.perf_counter()
    ttft = None
    chunks = 0
    usage = None
    with urllib.request.urlopen(req, timeout=180) as resp:
        for raw in resp:
            line = raw.decode("utf-8", "replace").strip()
            if not line.startswith("data:"):
                continue
            payload = line[5:].strip()
            if payload == "[DONE]":
                break
            try:
                obj = json.loads(payload)
            except json.JSONDecodeError:
                continue
            if obj.get("usage"):
                usage = obj["usage"]
            choices = obj.get("choices") or []
            if choices:
                delta = choices[0].get("delta", {})
                if delta.get("content"):
                    if ttft is None:
                        ttft = time.perf_counter() - t0
                    chunks += 1
    total = time.perf_counter() - t0
    completion_tokens = (usage or {}).get("completion_tokens") or chunks
    gen_time = total - (ttft or 0)
    if gen_time < 0.5:
        return {"ttft_s": round(ttft, 2) if ttft else None,
                "total_s": round(total, 2), "completion_tokens": completion_tokens,
                "tps": None, "chunks": chunks,
                "note": "burst (buffered flush), excluded"}
    if chunks <= 5:
        return {"ttft_s": round(ttft, 2) if ttft else None,
                "total_s": round(total, 2), "completion_tokens": completion_tokens,
                "tps": None, "chunks": chunks,
                "note": "no visible stream (reasoning-only?), excluded"}
    return {
        "ttft_s": round(ttft, 2) if ttft else None,
        "total_s": round(total, 2),
        "completion_tokens": completion_tokens,
        "tps": round(completion_tokens / gen_time, 1),
        "e2e_tps": round(completion_tokens / total, 1),
        "chunks": chunks,
    }


results = []
for i in range(N):
    r = run_once()
    results.append(r)
    tps_str = f"TPS={r['tps']} e2e={r.get('e2e_tps')}" if r["tps"] else f"TPS=n/a ({r.get('note','')})"
    print(f"run {i+1}: TTFT={r['ttft_s']}s  total={r['total_s']}s  "
          f"tokens={r['completion_tokens']}  chunks={r['chunks']}  {tps_str}")

tps_vals = [r["tps"] for r in results if r["tps"]]
print("\n--- summary ---")
print(f"model: {MODEL} (streaming)")
if tps_vals:
    print(f"valid runs   : {len(tps_vals)}/{N}")
    print(f"median TPS   : {statistics.median(tps_vals)}")
    print(f"mean TPS     : {round(statistics.mean(tps_vals),1)}")
    print(f"min/max      : {min(tps_vals)} / {max(tps_vals)}")
excluded = [r for r in results if not r["tps"]]
if excluded:
    print(f"excluded runs: {len(excluded)} ({', '.join(r.get('note','') for r in excluded)})")
