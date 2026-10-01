---
name: localai
description: Run or set up LocalAI for local OpenAI-compatible inference.
---

# LocalAI — local OpenAI-compatible inference (CPU-first)

LocalAI is a drop-in OpenAI-compatible REST server (LLMs, embeddings, image/audio/video generation) that runs fully local. Image generation uses Stable Diffusion backends (stablediffusion-ggml C++ or diffusers Python).

## When to use
- User wants a local/on-prem OpenAI-compatible endpoint ("localai", "stable diffusion", "image generation" + local/CPU/Docker context).
- Replacing OpenAI SDK base_url with a local server, or generating images without a cloud API.

## Hard-won user preference (do not repeat this mistake)
- CPU-ONLY by default on this machine (AMD Ryzen 7 7730U, NO NVIDIA GPU — nvidia-smi not installed; don't assume CUDA). User explicitly corrected: "i dont want gpu i only want cpu genration". Pull `localai/localai:latest` (CPU image), NOT `-gpu-hipblas` / `-gpu-nvidia-cuda-12` etc. GPU variants only if the user asks.
- Gallery auto-detects hardware, but for deterministic CPU use the plain image.

## Install & run (Docker)
1. `docker pull localai/localai:latest`
2. Run with persistent bind mounts — default run creates ANONYMOUS volumes that vanish on container recreation:
```bash
mkdir -p ~/.localai/{models,backends,data,configuration}
sudo docker run -d --name local-ai -p 8080:8080 \
  -v ~/.localai/models:/models \
  -v ~/.localai/backends:/backends \
  -v ~/.localai/data:/data \
  -v ~/.localai/configuration:/configuration \
  localai/localai:latest
```
3. Health check: `curl localhost:8080/v1/models` → `{"object":"list","data":[]}`.
4. The CLI binary inside the container is `/local-ai` (NOT on PATH).

## Fedora/SELinux bind-mount pitfall (VERIFIED)
- Symptom: server starts but `/v1/models` returns 500 `open //models: permission denied`; logs show `cannot read directory`, `error registering external backends`, watcher/traces errors.
- Cause: Enforcing SELinux labels host dirs `user_home_t`; container can't read them.
- Fix: `sudo chcon -Rt svirt_sandbox_file_t ~/.localai/models ~/.localai/backends ~/.localai/data ~/.localai/configuration` then `sudo docker restart local-ai`. (Alternative: mount with `:z`, e.g. `-v $HOME/.localai/models:/models:z`.)
- Any directory created later gets the wrong context again — re-apply chcon.

## Installing an image model
- Search gallery: `sudo docker exec local-ai /local-ai models list | grep -iE "stablediffusion|sd-|flux.1-ggml|animagine|dreamshaper|ltx"`
- CPU-friendly picks: `sd-1.5-ggml` (~2.1 GB Q4_0), `sd-3.5-medium-ggml`, `flux.1-dev-ggml`, `dreamshaper`, `ltx-2` (video).
- Install: `sudo docker exec local-ai /local-ai models install sd-1.5-ggml`
- TIMEOUT PATTERN: the download (HF GGUF ~2.1 GB) plus backend OCI pull (quay.io, e.g. `latest-cpu-stablediffusion-ggml`) takes several minutes. Run FOREGROUND with timeout 240–600. DO NOT run in background: `sudo` in a Hermes background process fails with "a terminal is required to read the password". A timed-out install is resumable — re-run the same command; the cached GGUF skips ahead to the backend pull.
- After install, the model may NOT appear in `/v1/models` until the container is restarted (server scanned configs at boot). Restart, then verify:
  `curl -s localhost:8080/v1/models` → `{"id":"sd-1.5-ggml",...}`.
- GGUF lands at `/models/<file>.gguf`; backend binary at `/backends/cpu-<backend>/`.

## Generate images (VERIFIED on CPU)
```bash
curl http://localhost:8080/v1/images/generations -H "Content-Type: application/json" \
  -d '{"prompt":"A cute baby sea otter","size":"256x256"}'
```
- Response JSON: `data[0].url` → `http://localhost:8080/generated-images/<id>.png`. Always download and check with `file <out.png>` (real PNG, don't assume).
- Extra API params: `step` (inference steps), `mode`. Negative prompt: split with `|` → `"a cat|blurry, deformed"`.
- CPU SPEED EXPECTATION (Ryzen 7): 256x256/25 steps ≈ 1 minute; 512x512 ≈ several minutes. Quick tests: 256x256 + fewer steps; final renders: larger sizes.
- Web UI at http://localhost:8080 (chat, model gallery install, image gen).

## Verify persistence / maintenance
- Model files persist in `~/.localai/models`, backends in `~/.localai/backends`. Helper: `~/.localai/manage.sh start|stop|restart|status|logs` (recreates container with proper mounts + chcon if missing) — copy from `templates/manage.sh`.
- `sudo usermod -aG docker painarise` requires a NEW shell to take effect — mention this to the user; otherwise docker commands need sudo forever.

## Support files
- `references/api-endpoints.md` — full image-generation API surface: text2img, image2img (base64), depth2img, img2vid (video), negative prompts, model YAML configs (stablediffusion-ggml + diffusers backends). Doc-derived unless labeled VERIFIED.