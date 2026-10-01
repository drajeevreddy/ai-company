# LocalAI image generation — API surface & model configs

Source: https://localai.io/docs/features/image-generation/ (Aug 2026). Items labeled VERIFIED were tested locally against LocalAI v4.8.2 (CPU, sd-1.5-ggml). Everything else is doc-derived — verify before relying on it.

## Endpoint
`POST /v1/images/generations` — OpenAI-compatible. OpenAI API docs: https://platform.openai.com/docs/api-reference/images/create

### Text to image (VERIFIED)
```bash
curl http://localhost:8080/v1/images/generations -H "Content-Type: application/json" \
  -d '{"prompt": "A cute baby sea otter", "size": "256x256"}'
```
- Additional API params: `mode`, `step`.
- Negative prompt: split the prompt with `|` (positive|negative):
```bash
-d '{"prompt": "floating hair, portrait, cute face, masterpiece|deformed, blurry, bad anatomy, text", "size": "256x256"}'
```

## Backends

### stablediffusion-ggml (CPU C++ — the CPU path; VERIFIED for basic workflow)
Based on https://github.com/leejet/stable-diffusion.cpp — every model that backend supports, LocalAI supports. Custom model YAML into the models dir:
```yaml
# stablediffusion.yaml
name: stablediffusion
backend: stablediffusion-ggml
parameters:
  model: gguf_model.gguf
step: 25
cfg_scale: 4.5
options:
- "clip_l_path:clip_l.safetensors"
- "clip_g_path:clip_g.safetensors"
- "t5xxl_path:t5xxl-Q5_0.gguf"
- "sampler:euler"
```
Steps for custom model: create YAML in models folder → download assets into models dir → start LocalAI.
Gallery one-liner: `local-ai run flux.1-dev-ggml` (FLUX on CPU).

Memory/device placement options (weights vs compute; mostly GPU-relevant but `backend:clip=cpu` can force CPU components):
| Option | Example | Meaning |
|---|---|---|
| `backend` | `backend:clip=cpu,vae=cuda0,diffusion=vulkan0` | compute backend per component (`te`, `vae`, `diffusion`, `controlnet`) |
| `params_backend` | `params_backend:diffusion=disk,clip=cpu` | where weights live: `cpu`/`disk` (mmap) |
| `max_vram` | `max_vram:8` or `-1` | VRAM budget (GiB), `-1` auto |
| `stream_layers` | `stream_layers:true` | streaming on top of max_vram |
| `rpc_servers` | `rpc_servers:host:port,...` | offload compute to RPC servers |

### diffusers (Python; GPU-first)
YAML with `backend: diffusers`, `pipeline_type` pick, e.g.:
```yaml
name: animagine-xl
backend: diffusers
parameters:
  model: Linaqruf/animagine-xl
f16: true
cuda: true
diffusers:
  pipeline_type: AutoPipelineForText2Image
```
Arbitrary extra params pass straight through as pipeline kwargs, e.g. `options: ["cfg_scale:6"]` → `pipe(prompt=..., size=..., cfg_scale=6)`.
Pipeline types seen in docs: StableVideoDiffusionPipeline, AutoPipelineForText2Image, VideoDiffusionPipeline, StableDiffusion3Pipeline, FluxPipeline, FluxTransformer2DModel, SanaPipeline.

## Image to image (img2img, diffusers backend, doc-derived)
YAML:
```yaml
name: stablediffusion-edit
parameters:
  model: nitrosocke/Ghibli-Diffusion
backend: diffusers
step: 25
cuda: true
f16: true
diffusers:
  pipeline_type: StableDiffusionImg2ImgPipeline
  enable_parameters: "negative_prompt,num_inference_steps,image"
```
Call: send base64 image in `file` field:
```bash
IMAGE_PATH=/path/to/your/image
(echo -n '{"file": "'; base64 $IMAGE_PATH; echo '", "prompt": "a sky background","size": "512x512","model": "stablediffusion-edit"}') |
curl -H "Content-Type: application/json" -d @- http://localhost:8080/v1/images/generations
```

### Flux Kontext (edit via ref_images, doc-derived)
`local-ai run flux.1-kontext-dev`
```bash
curl http://localhost:8080/v1/images/generations -H "Content-Type: application/json" -d '{
  "model": "flux.1-kontext-dev",
  "prompt": "change '"'"'flux.cpp'"'"' to '"'"'LocalAI'"'"'",
  "size": "256x256",
  "ref_images": ["https://raw.githubusercontent.com/leejet/stable-diffusion.cpp/master/assets/flux/flux1-dev-q8_0.png"]
}'
```

### Depth to image (doc-derived)
```yaml
name: stablediffusion-depth
parameters:
  model: stabilityai/stable-diffusion-2-depth
backend: diffusers
step: 50
f16: true
cuda: true
cfg_scale: 6
diffusers:
  pipeline_type: StableDiffusionDepth2ImgPipeline
  enable_parameters: "negative_prompt,num_inference_steps,image"
```
Call is the same base64-on-`"file"` pattern.

### Video (img2vid, txt2vid — GPU-heavy, doc-derived)
```yaml
name: img2vid
parameters:
  model: stabilityai/stable-video-diffusion-img2vid
backend: diffusers
step: 25
f16: true
cuda: true
diffusers:
  pipeline_type: StableVideoDiffusionPipeline
```
```yaml
name: txt2vid
parameters:
  model: damo-vilab/text-to-video-ms-1.7b
backend: diffusers
step: 25
f16: true
cuda: true
diffusers:
  pipeline_type: VideoDiffusionPipeline
  cuda: true
```
Call img2vid with `"file": "<URL>"`; call txt2vid with `"prompt"` only. Not recommended on CPU.