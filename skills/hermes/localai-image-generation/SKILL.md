---
name: localai-image-generation
description: Run LocalAI Stable Diffusion image gen on CPU in Docker.
---

# LocalAI Image Generation (CPU, Docker)

Set Stable Diffusion behind an OpenAI-compatible API (`/v1/images/generations`) using LocalAI in Docker, CPU-only.

## Current state (Aug 2026, user machine)
- LocalAI v4.8.2 container `local-ai` on port 8080, CPU image `localai/localai:latest`
- Model: `sd-1.5-ggml` (stable-diffusion-v1-5-pruned-emaonly Q4_0 GGUF, ~2 GB) — registered and generating
- Persistent bind mounts: `~/.localai/{models,backends,data,configuration}`
- Helper: `~/.localai/manage.sh` (start|stop|restart|status|logs|image [prompt] [size])

## 1. Pull CPU image (NOT gpu variants)
```bash
sudo docker pull localai/localai:latest
```

## 2. Run with persistent bind mounts
```bash
mkdir -p ~/.localai/{models,backends,data,configuration}
sudo docker run -d --name local-ai \
  -p 8080:8080 \
  -v ~/.localai/models:/models \
  -v ~/.localai/backends:/backends \
  -v ~/.localai/data:/data \
  -v ~/.localai/configuration:/configuration \
  localai/localai:latest
```

## 3. SELinux (Fedora) — REQUIRED, else permission denied
Container runs as root but Fedora blocks host bind mounts with `user_home_t` context:
```bash
sudo chcon -Rt svirt_sandbox_t ~/.localai/{models,backends,data,configuration}
sudo docker restart local-ai
```
Symptom: `open //models: permission denied` in logs, `/v1/models` returns HTTP 500; models list empty.

## 4. Install model (CPU = ggml backend)
Binary inside container: `/local-ai`.
```bash
# list gallery image models
sudo docker exec local-ai /local-ai models list | grep -iE "sd-|flux|dreamshaper|animagine"

# install SD 1.5 GGUF (~2 GB + C++ backend from quay.io)
sudo docker exec local-ai /local-ai models install sd-1.5-ggml
```
- Downloads to `/models/stable-diffusion-v1-5-pruned-emaonly-Q4_0.gguf`; backend lands in `/backends/cpu-stablediffusion-ggml/`
- Long installs: `sudo docker exec` needs a TTY, run foreground with `timeout=600` (background fails: "sudo: a terminal is required")
- After install, RESTART container — new model YAML in /models only scanned at boot: `sudo docker restart local-ai`
- Other CPU models: `flux.1-dev-ggml`, `sd-3.5-medium-ggml`, `sd-3.5-large-ggml`, `dreamshaper`, `wan-2.1-t2v-1.3b-ggml` (video)

## 5. Generate images (OpenAI-compatible)
```bash
curl http://localhost:8080/v1/images/generations -H "Content-Type: application/json" \
  -d '{"prompt": "a cute baby sea otter", "size": "512x512"}'
# → {"data":[{"url":"http://localhost:8080/generated-images/<id>.png"}]}; GET that URL for the PNG
```
- Negative prompt: `positive|negative` split with `|`
- Speed: `"step": 20` (default 25); 256x256 ≈ 56s, 512x512 = minutes on CPU
- img2img: body `{"file": "<base64>", "prompt": ..., "model": "sd-1.5-ggml"}`
- Web UI: http://localhost:8080 (chat + gallery browse)

## Pitfalls
1. SELinux — after new bind-mount dirs or chown, re-run `chcon` (step 3), else silent 500s.
2. OOM — `fatal error: runtime: out of memory` killed container on this 15 GB box (9+ GB used by other workloads). Fix: `sudo docker start local-ai`. CPU SD at 512x512 can spike > 4 GB RAM.
3. Restart needed after `models install` (config watcher needs SELinux label).
4. Persist `/backends` too — else every recreate re-pulls C++ backend from quay.io.
5. Docker pull flakiness here (CloudFront resets) — retry; layer cache resumes.
6. If container was removed: bind mounts preserve data; just recreate + `chcon`.
7. Docs: https://localai.io/docs/features/image-generation/ (Flux, img2img, depth2img, txt2vid/img2vid via diffusers = GPU-oriented; ggml for CPU).