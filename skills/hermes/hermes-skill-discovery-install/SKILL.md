---
name: hermes-skill-discovery-install
description: Batch-install Hermes skills from GitHub with security scans.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [skills, discovery, installation, github, security-scan, batch]
    related_skills: [hermes-agent, gstack-install, hermes-agent-skill-authoring, hermes-skill-library-portability]
---

# Hermes Skill Discovery & Installation

## Overview

Discover community skills on GitHub, vet them, and install them in batch while handling Hermes' security scanner verdicts. This workflow turns "I need more skills" into a reproducible, auditable process.

## When to Use

- User asks "find me skills for X" or "install all the X skills"
- You need to expand the agent's capability surface for a new domain
- Setting up a fresh Hermes environment with a curated skill set
- Auditing what community skills exist for a category

## Don't Use For

- Installing a single known skill by URL (use `hermes skills install` directly)
- Managing in-repo skills (see `hermes-agent-skill-authoring`)
- Bundled/builtin skills (those ship with Hermes)
- Exporting, backing up, or migrating an existing library to another machine (see `hermes-skill-library-portability`)

## Discovery Workflow

### 1. Search for Skill Repositories

Use GitHub's search API with these high-yield queries:

```bash
# Official curated lists (best starting point)
curl -s "https://api.github.com/search/repositories?q=awesome-hermes-skills&sort=stars&per_page=5"

# By category (replace CATEGORY)
curl -s "https://api.github.com/search/repositories?q=hermes+skill+CATEGORY&per_page=20"
curl -s "https://api.github.com/search/repositories?q=skill+in:name,description+hermes+CATEGORY&per_page=20"
```

**High-yield categories to try:** `coding`, `debugging`, `devops`, `security`, `testing`, `refactoring`, `architecture`, `documentation`, `database`, `api`, `frontend`, `backend`, `research`, `writing`, `analysis`.

### 2. Find SKILL.md Files in a Repo

Once you have a candidate repo, check for installable skills:

```bash
curl -s "https://api.github.com/repos/OWNER/REPO/git/trees/HEAD?recursive=1" | \
  jq -r '.tree[] | select(.path | endswith("SKILL.md")) | .path'
```

### 3. Inspect Frontmatter Before Installing

```bash
curl -s "https://raw.githubusercontent.com/OWNER/REPO/main/PATH/SKILL.md" | head -20
```

Verify: `name`, `description`, `version`, `metadata.hermes.tags` exist. Skip skills with missing/broken frontmatter.

## Batch Installation

### 4. Parallel Install with Security Scan Handling

Hermes runs a security scan on every community skill. Verdicts:

| Verdict | Meaning | Action |
|---------|---------|--------|
| **SAFE** | Clean | Auto-installs |
| **CAUTION** | Minor findings (e.g., `sudo`, unpinned npm) | Re-run with `--force` if acceptable |
| **DANGEROUS** | Critical findings (exfiltration, obfuscation) | **Blocked** — `--force` does NOT override. Investigate manually or skip. |

**Batch install script template:**

```bash
#!/bin/bash
# batch-install-skills.sh
set -euo pipefail

# Array of: "REPO  PATH/SKILL.md  CATEGORY"
SKILLS=(
  "owner/repo  skills/skill-name/SKILL.md  autonomous-ai-agents"
  # ... more entries
)

for entry in "${SKILLS[@]}"; do
  read -r repo path category <<< "$entry"
  url="https://raw.githubusercontent.com/${repo}/main/${path}"
  hermes skills install "$url" --category "$category" --yes &
done
wait
echo "All installs completed"
```

### 5. Handle CAUTION Verdicts Selectively

For skills blocked with CAUTION that you still want:

```bash
hermes skills install "URL" --category autonomous-ai-agents --yes --force
```

**Only force-install when you've read the skill and understand the finding.** Common CAUTION patterns:
- `sudo_usage` — skill runs sudo (common in k8s benchmarking)
- `unpinned_pip_install` — installs packages without version pinning
- `persistence_cron` — adds cron entries (common in inventory skills)

### 6. Verify Installation

```bash
hermes skills list | grep "CATEGORY"
```

Check each installed skill has `enabled` status.

## Curation Heuristics

### Prefer These Sources (in order)

1. **ZeroPointRepo/awesome-hermes-skills** — curated list with install commands
2. **Hermes-native ports** (e.g., `srkhorde/ponytail` from `DietrichGebert/ponytail`)
3. **High-star orgs** with clear skill directories: `mattpocock/skills`, `wondelai/skills`, `wordbricks/skills`
4. **Domain-specific skill packs**: `smartcontractkit/chainlink-agent-skills`, `Mukul975/Anthropic-Cybersecurity-Skills`

### Avoid

- Repos with no `SKILL.md` files at all (false positives from search)
- Skills with `DANGEROUS` verdicts you can't justify
- Skills that duplicate builtin/hermes-agent functionality
- Narrow one-off skills — prefer class-level skills that compose

## Token Cost Awareness

Every skill in `autonomous-ai-agents` adds ~160 chars (≈40 tokens) to the **per-turn system prompt skill index**. 100 skills = ~4,000 tokens/turn baseline.

**Mitigation:**
- Disable unused categories via `hermes skills config`
- Keep only skills you actually invoke
- Use `caveman` / `ponytail` for token compression when needed

## Common Pitfalls

1. **Installing everything from a massive repo** (e.g., 817 cybersecurity skills) — bloats prompt, most go unused. Curate a focused subset.

2. **Ignoring security scan output** — DANGEROUS verdicts indicate real risks (exfiltration patterns, obfuscated code). Read the finding before forcing.

3. **Not checking frontmatter first** — broken frontmatter fails install; wasted API calls.

4. **Parallel installs without `wait`** — race conditions on the quarantine directory. Always `wait` after firing background installs.

5. **Forgetting `--category`** — skills land in wrong category, harder to manage.

## Verification Checklist

- [ ] Searched GitHub with category-specific queries
- [ ] Identified repos with actual `SKILL.md` files
- [ ] Inspected frontmatter of each candidate
- [ ] Batch-installed with parallel jobs + `wait`
- [ ] Reviewed security scan verdicts for each
- [ ] Force-installed only justified CAUTION skills
- [ ] Verified all show `enabled` in `hermes skills list`
- [ ] Total skill count is sustainable for your token budget

## One-Shot Recipes

### Install the "Matt Pocock Engineering" Pack

```bash
SKILLS=(
  "mattpocock/skills  skills/engineering/code-review/SKILL.md  autonomous-ai-agents"
  "mattpocock/skills  skills/engineering/diagnosing-bugs/SKILL.md  autonomous-ai-agents"
  "mattpocock/skills  skills/engineering/implement/SKILL.md  autonomous-ai-agents"
  "mattpocock/skills  skills/engineering/improve-codebase-architecture/SKILL.md  autonomous-ai-agents"
  "mattpocock/skills  skills/engineering/research/SKILL.md  autonomous-ai-agents"
  "mattpocock/skills  skills/engineering/tdd/SKILL.md  autonomous-ai-agents"
  "mattpocock/skills  skills/engineering/to-spec/SKILL.md  autonomous-ai-agents"
  "mattpocock/skills  skills/engineering/to-tickets/SKILL.md  autonomous-ai-agents"
  "mattpocock/skills  skills/engineering/triage/SKILL.md  autonomous-ai-agents"
  "mattpocock/skills  skills/engineering/wayfinder/SKILL.md  autonomous-ai-agents"
  "mattpocock/skills  skills/engineering/wizard/SKILL.md  autonomous-ai-agents"
  "mattpocock/skills  skills/engineering/codebase-design/SKILL.md  autonomous-ai-agents"
  "mattpocock/skills  skills/engineering/domain-modeling/SKILL.md  autonomous-ai-agents"
  "mattpocock/skills  skills/engineering/prototype/SKILL.md  autonomous-ai-agents"
  "mattpocock/skills  skills/engineering/resolving-merge-conflicts/SKILL.md  autonomous-ai-agents"
)
for entry in "${SKILLS[@]}"; do
  read -r repo path cat <<< "$entry"
  hermes skills install "https://raw.githubusercontent.com/${repo}/main/${path}" --category "$cat" --yes &
done
wait
```

### Install the "Wondelai Strategy/Design" Pack

```bash
SKILLS=(
  "wondelai/skills  clean-architecture/SKILL.md  autonomous-ai-agents"
  "wondelai/skills  clean-code/SKILL.md  autonomous-ai-agents"
  "wondelai/skills  domain-driven-design/SKILL.md  autonomous-ai-agents"
  "wondelai/skills  refactoring-patterns/SKILL.md  autonomous-ai-agents"
  "wondelai/skills  system-design/SKILL.md  autonomous-ai-agents"
  "wondelai/skills  team-topologies/SKILL.md  autonomous-ai-agents"
  "wondelai/skills  pragmatic-programmer/SKILL.md  autonomous-ai-agents"
  "wondelai/skills  working-with-legacy-code/SKILL.md  autonomous-ai-agents"
  "wondelai/skills  software-design-philosophy/SKILL.md  autonomous-ai-agents"
  "wondelai/skills  ddia-systems/SKILL.md  autonomous-ai-agents"
  "wondelai/skills  high-output-management/SKILL.md  autonomous-ai-agents"
  "wondelai/skills  lean-analytics/SKILL.md  autonomous-ai-agents"
  "wondelai/skills  lean-startup/SKILL.md  autonomous-ai-agents"
  "wondelai/skills  jobs-to-be-done/SKILL.md  autonomous-ai-agents"
  "wondelai/skills  mom-test/SKILL.md  autonomous-ai-agents"
  "wondelai/skills  obviously-awesome/SKILL.md  autonomous-ai-agents"
  "wondelai/skills  one-page-marketing/SKILL.md  autonomous-ai-agents"
  "wondelai/skills  good-strategy-bad-strategy/SKILL.md  autonomous-ai-agents"
  "wondelai/skills  blue-ocean-strategy/SKILL.md  autonomous-ai-agents"
)
# ... same parallel install pattern
```

### Install Curated Cybersecurity Auditing Pack

```bash
CYBER=(
  "Mukul975/Anthropic-Cybersecurity-Skills  skills/performing-vulnerability-scanning-with-nessus/SKILL.md  autonomous-ai-agents"
  "Mukul975/Anthropic-Cybersecurity-Skills  skills/performing-container-security-scanning-with-trivy/SKILL.md  autonomous-ai-agents"
  "Mukul975/Anthropic-Cybersecurity-Skills  skills/integrating-sast-into-github-actions-pipeline/SKILL.md  autonomous-ai-agents"
  "Mukul975/Anthropic-Cybersecurity-Skills  skills/integrating-dast-with-owasp-zap-in-pipeline/SKILL.md  autonomous-ai-agents"
  "Mukul975/Anthropic-Cybersecurity-Skills  skills/implementing-semgrep-for-custom-sast-rules/SKILL.md  autonomous-ai-agents"
  "Mukul975/Anthropic-Cybersecurity-Skills  skills/testing-api-security-with-owasp-top-10/SKILL.md  autonomous-ai-agents"
  "Mukul975/Anthropic-Cybersecurity-Skills  skills/performing-web-application-penetration-test/SKILL.md  autonomous-ai-agents"
  "Mukul975/Anthropic-Cybersecurity-Skills  skills/auditing-aws-s3-bucket-permissions/SKILL.md  autonomous-ai-agents"
  "Mukul975/Anthropic-Cybersecurity-Skills  skills/auditing-cloud-with-cis-benchmarks/SKILL.md  autonomous-ai-agents"
  "Mukul975/Anthropic-Cybersecurity-Skills  skills/performing-aws-account-enumeration-with-scout-suite/SKILL.md  autonomous-ai-agents"
  "Mukul975/Anthropic-Cybersecurity-Skills  skills/securing-aws-iam-permissions/SKILL.md  autonomous-ai-agents"
  "Mukul975/Anthropic-Cybersecurity-Skills  skills/securing-aws-lambda-execution-roles/SKILL.md  autonomous-ai-agents"
  "Mukul975/Anthropic-Cybersecurity-Skills  skills/securing-kubernetes-on-cloud/SKILL.md  autonomous-ai-agents"
  "Mukul975/Anthropic-Cybersecurity-Skills  skills/implementing-secrets-management-with-vault/SKILL.md  autonomous-ai-agents"
  "Mukul975/Anthropic-Cybersecurity-Skills  skills/implementing-secrets-scanning-in-ci-cd/SKILL.md  autonomous-ai-agents"
  "Mukul975/Anthropic-Cybersecurity-Skills  skills/performing-red-team-phishing-with-gophish/SKILL.md  autonomous-ai-agents"
  "Mukul975/Anthropic-Cybersecurity-Skills  skills/continuous-llm-red-teaming-with-promptfoo/SKILL.md  autonomous-ai-agents"
  "Mukul975/Anthropic-Cybersecurity-Skills  skills/testing-prompt-injection-in-rag-pipelines/SKILL.md  autonomous-ai-agents"
  "Mukul975/Anthropic-Cybersecurity-Skills  skills/performing-soc2-type2-audit-preparation/SKILL.md  autonomous-ai-agents"
  "Mukul975/Anthropic-Cybersecurity-Skills  skills/implementing-iso-27001-information-security-management/SKILL.md  autonomous-ai-agents"
  "Mukul975/Anthropic-Cybersecurity-Skills  skills/implementing-pci-dss-compliance-controls/SKILL.md  autonomous-ai-agents"
  "Mukul975/Anthropic-Cybersecurity-Skills  skills/implementing-gdpr-data-protection-controls/SKILL.md  autonomous-ai-agents"
)
# ... same parallel install pattern
# Note: some will need --force for CAUTION verdicts
```

## References

- `hermes skills install --help` — CLI flags
- `hermes skills config` — enable/disable per platform
- `hermes skills browse` — browse hub catalog
- ZeroPointRepo/awesome-hermes-skills — canonical curated list
- Security scanner rules: `skills-guard-v1` (checks: `sudo_usage`, `unpinned_pip_install`, `persistence_cron`, `env_exfil_curl`, `fake_policy`, `echo_pipe_exec`, `python_subprocess`, `allowed_tools_field`)