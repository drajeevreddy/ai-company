---
name: blynk-prompt
description: Load when writing BlynkAds AI pipeline prompts with schemas.
---

# BlynkAds Prompts Skill

## Usage
Load when writing or updating any AI pipeline prompt. Ensures consistency with schemas and versioning.

## Prompt Registry
```
prompts/
├── prompt-enhancement/     # Raw prompt → EnhancedBrief
├── targetiq-meta/          # EnhancedBrief → Meta targeting_spec
├── targetiq-google/        # EnhancedBrief → Google audience signals
├── creative-static/        # Concept → Flux/SDXL prompts
├── creative-video/         # Script → Runway/Kling/Luma prompts
├── creative-copy/          # Brief → Ad copy variants
├── landing-page/           # Brief → Landing page content
├── creative-refresh/       # Winners → New concepts
├── closed-loop/            # Lead feedback → Targeting patches
└── eval/                   # Evaluation harness
```

## Each Prompt Has
- `v1.0.system.md` — System prompt
- `v1.0.user.md` — User template with {{variables}}
- `schema.json` — JSON Schema for output validation

## Workflow
1. Read relevant prompt files before modifying AI pipeline code
2. Update both prompt + schema together
3. Run `bun run prompts/eval/runner.ts` after changes
4. Version bump: `v1.0` → `v1.1` for backward-compatible, `v2.0` for breaking

## Key Principles
- All outputs MUST be valid JSON (enforced by `response_format: json_object`)
- Temperature: 0.2 for consistency
- Model: GPT-4o / Claude 3.5 Sonnet for structured tasks
- Schemas validated at runtime via Zod

## References
- `references/eval-harness.md` — Prompt evaluation harness for regression testing