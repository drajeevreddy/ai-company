---
name: gstack-install
description: "Install gstack AI engineering skills into Hermes."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [GStack, Skill-Harness, AI-Engineering, Third-Party]
    related_skills: [hermes-agent, opencode, cursor-agent, command-code, vibe, mimo, claude-code, codex]
---

# gstack Install for Hermes

Install Garry Tan's gstack AI engineering skill harness into Hermes. gstack adds 54+ specialist skills (office-hours, plan-ceo-review, review, qa, ship, cso, browse, etc.) to any compatible agent harness.

## Prerequisites

- Git, Bun v1.0+, Node.js (Windows only)
- Hermes on PATH

## Install

```bash
# Clone
git clone --single-branch --depth 1 https://github.com/garrytan/gstack.git ~/gstack
cd ~/gstack && bun install

# Generate Hermes skill docs
bun run gen:skill-docs --host hermes

# Create runtime dirs
mkdir -p ~/.hermes/skills/gstack/{bin,browse/dist,browse/bin,design/dist,gstack-upgrade,review,specialists,qa/templates,qa/references,plan-devex-review}

# Symlink runtime assets
ln -sf ~/gstack/bin ~/.hermes/skills/gstack/bin
ln -sf ~/gstack/browse/dist ~/.hermes/skills/gstack/browse/dist
ln -sf ~/gstack/browse/bin ~/.hermes/skills/gstack/browse/bin
ln -sf ~/gstack/design/dist ~/.hermes/skills/gstack/design/dist
ln -sf ~/gstack/ETHOS.md ~/.hermes/skills/gstack/ETHOS.md
ln -sf ~/gstack/review/checklist.md ~/.hermes/skills/gstack/review/checklist.md
ln -sf ~/gstack/review/TODOS-format.md ~/.hermes/skills/gstack/review/TODOS-format.md
ln -sf ~/gstack/review/specialists ~/.hermes/skills/gstack/review/specialists
ln -sf ~/gstack/qa/templates ~/.hermes/skills/gstack/qa/templates
ln -sf ~/gstack/qa/references ~/.hermes/skills/gstack/qa/references
ln -sf ~/gstack/plan-devex-review/dx-hall-of-fame.md ~/.hermes/skills/gstack/plan-devex-review/dx-hall-of-fame.md
ln -sf ~/gstack/gstack-upgrade/SKILL.md ~/.hermes/skills/gstack/gstack-upgrade/SKILL.md

# Symlink each skill directory
for d in ~/gstack/.hermes/skills/gstack-*/; do
  name=$(basename "$d")
  target="$HOME/.hermes/skills/$name"
  [ -L "$target" ] || [ ! -e "$target" ] && ln -sf "$d" "$target"
done
```

## Verify

```bash
ls ~/.hermes/skills/gstack/ | head
```

## Update

```bash
cd ~/gstack && git pull && bun install
bun run gen:skill-docs --host hermes
# Re-run symlink steps above
```

## Pitfalls

- Hermes is NOT a first-class `./setup --host` target — the setup script exits early. Use `gen:skill-docs` manually.
- Missing `bin/` or `browse/dist/` symlinks are the most common failure mode.
- The `gstack` runtime dir needs symlinks to `bin/`, `browse/dist/`, `review/`, `qa/`, etc. for skills that reference runtime assets.
