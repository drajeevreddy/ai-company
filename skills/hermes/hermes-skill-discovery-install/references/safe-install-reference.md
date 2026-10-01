# Safe Hermes Skill Install Reference

This reference captures the verified install set and constraints from a real batch discovery session, so future agents can reproduce the working subset without re-running blocked skills.

## Verified Working Repo Set

### Engineering / Design
- `mattpocock/skills` — code-review, diagnosing-bugs, implement, improve-codebase-architecture, codebase-design, domain-modeling, to-spec, to-tickets, tdd
- `wondelai/skills` — system-design, pragmatic-programmer, ddia-systems, clean-code
- `conorbronsdon/avoid-ai-writing` — avoid-ai-writing

### Marketing
- `hyperfx-ai/marketing-skills` — meta-ads, linkedin, tiktok, analytics-insights, brand-context
- `social-media-skills/skills` — content-calendar, competitor-analysis, engagement-routine, community-management

### Security / Audit (SAFE / CAUTION-only)
- `Mukul975/Anthropic-Cybersecurity-Skills` — implementing-secrets-scanning-in-ci-cd, analyzing-security-logs-with-splunk
- `Zyrexnn/Cybermes` — redteam-mindset, hunt-sqli, hunt-xss, hunt-idor

## Known Blocked Skills (DANGEROUS; --force does NOT override)

These were blocked during batch install and should not be retried without manual review:
- `x-glacier/kali-pentest`
- `Zyrexnn/Cybermes` bug-bounty, hunt-ssrf, hunt-auth-bypass, hunt-rce, hunt-api-misconfig, web2-recon, offensive-osint, hunt-llm-ai

## Resilient Install Pattern

Use this shell pattern when installing multiple skills in batch:

```bash
for entry in "${SKILLS[@]}"; do
  read -r repo path category <<< "$entry"
  url="https://raw.githubusercontent.com/${repo}/main/${path}"
  hermes skills install "$url" --category "$category" --yes || true
done
```

This avoids aborting the whole batch on one fetch or scan error.
