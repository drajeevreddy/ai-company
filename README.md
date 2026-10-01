# 🏢 AI Company Ecosystem

> Complete AI company infrastructure - One command setup for cybersecurity, development, and AI automation

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Stars](https://img.shields.io/github/stars/animeprints/ai-company)](https://github.com/animeprints/ai-company/stargazers)
[![Forks](https://img.shields.io/github/forks/animeprints/ai-company)](https://github.com/animeprints/ai-company/network)

---

## 🧠 Skill Library

This repo also carries the consolidated skill library from every local agent CLI —
**555 unique skills** across 8 roots (hermes, claude, codex,
commandcode, cursor, agents, muse, gstack). Exact duplicates were merged; cross-CLI
aliases are recorded in `_aliases.json`.

```
skills/<cli>/<skill>/        # SKILL.md + references/, templates/, scripts/, assets/
SKILLS-INDEX.md              # every skill with its description
_aliases.json                # which other CLIs carry the same skill
```

See `SKILLS-INDEX.md` for the full list.

---

## 🧬 Agent Brain

The operating brain — not skills, but the doctrine and the record. An Obsidian vault
under `brain/`.

```
brain/Ai Agent Brain/
├── 00-Agent-Brain-Index.md   vault entry point
├── System/                   operating doctrine — Astra OS, Writing Voice,
│                             Anti-Slop-Prose, Code-Quality-Bar, Ponytail,
│                             Award-Winning-Design, GitHub-Skills
├── Skills/                   distilled lessons from real builds, plus the
│                             per-area hub notes
├── Projects/                 per-project records (Crestorflow, DocCare/EndoCare,
│                             Quivane)
├── Agents/                   agent definitions
└── sources/                  source material the doctrine was distilled from
```

Start at `brain/Ai Agent Brain/00-Agent-Brain-Index.md`.

> This vault names real client engagements and carries business detail. It lives here
> deliberately, in a public repo, by the owner's decision.

---

## 🚀 Quick Start (One Command)

```bash
# Install EVERYTHING - ~150 skills + tools
curl -sSL https://raw.githubusercontent.com/animeprints/ai-company/main/install-all-skills.sh | bash
```

Or clone manually:

```bash
git clone https://github.com/animeprints/ai-company.git ~/ai-company
cd ~/ai-company
```

---

## 📦 What's Included (9 Files)

| File | Purpose |
|------|---------|
| `install-all-skills.sh` | ⭐ One-tap install ~150 skills |
| `skills-manifest.md` | Complete list of all skills |
| `README.md` | This file |
| `skills-reference.md` | Skills by category |
| `ai-ecosystem-strategic-report.md` | Strategy + 90K skills ecosystem |
| `cybersecurity-playbook.md` | Red/Blue team operations |
| `ai-development-guide.md` | LangChain, CrewAI, MCP guides |
| `install.sh` | Basic installer |
| `skills-backup/install-ai-company.sh` | Quick setup |

---

## 🎯 Skills Overview (~150 Skills)

### By Category

| Category | Count | Top Skills |
|----------|-------|-----------|
| 🎨 Frontend & Design | 12 | frontend-design, shadcn, vercel-react-best-practices |
| 🤖 AI & Agents | 18 | microsoft-foundry, supabase, firebase, claude-api |
| 🌥️ Cloud & DevOps | 15 | azure-kubernetes, azure-cost, azure-deploy |
| 🔒 Security | 8 | openclaw-secure-linux-cloud, systematic-debugging |
| 📊 Marketing | 20 | copywriting, seo-audit, paid-ads, cold-email |
| 📄 Productivity | 15 | pdf, xlsx, pptx, docx, firecrawl |
| 🔧 Tools | 20 | find-skills, mcp-builder, deploy-to-vercel |
| 🧠 Workflow | 15 | brainstorming, writing-plans, test-driven-development |
| 📚 Next.js/React | 8 | next-best-practices, react-view-transitions |
| 🎯 Specialty | 15 | soultrace, remotion-best-practices, grill-me |

**Total: ~150 skills**

---

## 🛠️ Installation

### Prerequisites
```bash
- Python 3.8+
- Node.js 18+
- Docker (for PentAGI)
```

### Full Install
```bash
# One command to rule them all
curl -sSL https://raw.githubusercontent.com/animeprints/ai-company/main/install-all-skills.sh | bash
```

### Manual Install
```bash
# Clone repo
git clone https://github.com/animeprints/ai-company.git ~/ai-company

# Install specific category
cd ~/ai-company
bash install.sh
```

---

## 🔐 Cybersecurity Module

### Tools Included
| Tool | Purpose |
|------|---------|
| **PentAGI** | Autonomous AI pentesting (16.5K stars) |
| Metasploit | Exploitation framework |
| Nuclei | Vulnerability scanning |
| Burp Suite | Web testing |

### Quick Start PentAGI
```bash
docker pull vxcontrol/pentagi
docker run -d -p 8080:8080 \
  -e OPENAI_API_KEY=sk-... \
  vxcontrol/pentagi
# Access at http://localhost:8080
```

### Manual Tools
```bash
# Recon
nmap -sV target.com
amass enum -passive -d target.com

# Vulnerability
nuclei -u target.com -severity critical,high

# Exploitation
msfconsole
```

---

## 🤖 AI Agent Frameworks

| Framework | Install | Best For |
|----------|---------|---------|
| **LangGraph** | `pip install langgraph` | Complex workflows |
| **CrewAI** | `pip install crewai` | Multi-agent teams |
| **AutoGen** | `pip install pyautogen` | Microsoft ecosystem |
| **OpenAI SDK** | `pip install openai-agents` | GPT-native |

---

## 🔌 MCP Servers (12,000+)

### Official (Anthropic)
```bash
npx @anthropic-ai/mcp-server-filesystem /path
npx @anthropic-ai/mcp-server-github
npx @anthropic-ai/mcp-server-postgres
npx @anthropic-ai/mcp-server-brave-search
```

### Python
```bash
pip install mcp-server-fetch
pip install mcp-server-sqlite
```

### Top Community
- Notion, Slack, Firecrawl, Linear, Sentry, Docker

---

## 📚 Documentation

| File | Description |
|------|------------|
| [skills-manifest.md](./skills-manifest.md) | Complete skill inventory with install commands |
| [skills-reference.md](./skills-reference.md) | Skills organized by category |
| [ai-development-guide.md](./ai-development-guide.md) | AI dev tutorials |
| [cybersecurity-playbook.md](./cybersecurity-playbook.md) | Red/Blue team guides |
| [ai-ecosystem-strategic-report.md](./ai-ecosystem-strategic-report.md) | Industry analysis |

---

## 🎯 Use Cases

### For Startups
```bash
# Cybersecurity → PentAGI
# Development → LangChain + MCP
# Marketing → CrewAI + copywriting
# Operations → automation
```

### For Enterprises
```bash
# Azure → microsoft-foundry + azure-kubernetes
# AWS → AWS MCP + Pacu
# Google → Google ADK + Vertex
# Multi-cloud → LangGraph with any LLM
```

---

## 📖 Usage After Install

```bash
# List installed skills
skill list

# Find more skills
skill find "pdf"

# Run a skill
skill run owner/repo

# Quick commands
ai-company        # Go to workspace
ai-report        # View strategic report  
ai-skills       # View skills manifest
ai-sec          # View security playbook
ai-dev         # View AI dev guide
pentagi         # Start PentAGI (requires Docker)
```

---

## 🤝 Contributing

1. Fork the repo
2. Add skills to manifest
3. Update README
4. Submit PR

---

## 📄 License

MIT License - Build freely!

---

## 🔗 Resources

- **Repo**: https://github.com/animeprints/ai-company
- **Skills**: https://skills.sh
- **MCP Registry**: https://mcpindex.net
- **PentAGI**: https://pentagi.com
- **LangChain**: https://python.langchain.com
- **CrewAI**: https://docs.crewai.com

---

*Built with 🔥 by AI Company Ecosystem*

![Stars](https://img.shields.io/github/stars/animeprints/ai-company)
![Forks](https://img.shields.io/github/forks/animeprints/ai-company)