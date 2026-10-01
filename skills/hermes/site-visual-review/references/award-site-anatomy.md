# Award-Site Anatomy — "Remake Lusion" Knowledge Bank

Condensed from a design-specialist review session (Aug 2026): user asked for the world's best agency sites with unforgettable 3D hero experiences, then asked what it would take to remake Lusion. Use when asked to judge/rank immersive sites, or scope a rebuild of one.

## Top-tier reference sites (validated by live screenshot review)

| Site | URL | Signature | Review note |
|---|---|---|---|
| Lusion | https://lusion.co/ | Whole site IS a real-time 3D engine: physics objects, particle fields, all cursor-reactive, rendered live (no video fakes) | Awwwards Site of the Year; global benchmark for 3D-as-identity |
| Resn | https://resn.co.nz/ | Faceted black crystal hero, chromatic-aberration edges, "CLICK & HOLD" interaction cue | Interaction-as-design: visitor becomes participant |
| Noomo | https://noomoagency.com/ | Massive kinetic display type + 3D chrome/glass forms floating through letters, soft gradient atmosphere | Best "digital marketing agency" balance of wow + clarity |
| Exo Ape | https://www.exoape.com/ | Cinematic editorial, giant cropped typography over photography, buttery scroll choreography | Gorgeous but photo/motion-led, not true 3D |
| Obys | https://obys.agency/ | Brutalist type experiments, live-clock details | Art-direction brilliance |
| Active Theory | https://activetheory.net/ | Blocks automated/headless browsers ("Not Supported" title) | Legendary WebGL shop; verify manually in a normal browser |

## What separates "nice" from "unforgettable" (the 30%)

- The 3D is INTERACTIVE, not decorative — cursor forces, click-and-hold, physics response
- One dominant hero idea per site (crystal / physics world / giant type+glass); never five competing effects
- Typography does heavy lifting alongside the 3D — huge scale, tight tracking
- Motion has personality: hand-tuned easing, inertia, response to input
- Holding 60fps on mid-range hardware, graceful mobile fallback

## What Lusion-level actually requires (scoping a remake)

Stack: custom Three.js/WebGL (moving to WebGPU) rendering layer; GPGPU particle systems (FBO ping-pong); real-time rigid-body physics with cursor forces; custom GLSL + post-FX chain (DoF, bloom, grain, chromatic aberration); virtual scroll (Lenis) driving DOM + 3D camera together; persistent WebGL canvas across route transitions (scenes morph, never "load"); Blender → glTF+Draco+KTX2 asset pipeline; adaptive resolution/instancing/LOD perf engineering.

Team at true level: 1–2 creative devs (shader math — the rare expensive role, the whole ballgame), 3D artist, art director, frontend eng, optional sound designer.

Cost tiers (India-market rates, 2026):
- DIY (agent-scaffolded): near-zero cash, 3–5 months nights-and-weekends to full quality; 2–4 weeks to an interactive hero POC
- Freelance creative dev: ₹2.5–8k/hr → hero-only ₹2–6L (3–6 wks); full site ₹15–50L (3–6 months)
- Agency: $100–300k+

Templates/Spline reach ~70% of the look, ~none of the feel.

Phased build (works well as an engagement shape):
1. wk1: Next.js + react-three-fiber + Lenis skeleton, cursor-reactive GPU particle hero
2. wk2–3: signature hero object — physics + custom GLSL + post-FX
3. wk4: scroll choreography + persistent-canvas route transitions
4. wk5: perf pass — instancing, adaptive DPR, mobile fallback, sound
5. wk6+: typography, content, polish loop

Learning path if shaders are new: Bruno Simon's Three.js Journey (standard on-ramp), 4–8 weeks part-time to "dangerous".

## Session capture workflow

See SKILL.md for the Playwright capture method. For ranking tasks: capture hero + settle shots per candidate, review each with a specific design-specialist prompt, synthesize a ranked verdict + transferable patterns. Save shots to a session scratch dir (e.g. ~/agencyscout/shots/) so the user can re-inspect.
