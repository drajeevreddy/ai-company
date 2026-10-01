# 🏢 AI Company Ecosystem

> The agent's skills, its operating doctrine, and the playbooks — consolidated from every
> local agent CLI into one place.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Skills](https://img.shields.io/badge/skills-553-blue)](./SKILLS-INDEX.md)
[![CLIs](https://img.shields.io/badge/source%20CLIs-8-informational)](#skill-library)

---

## What this repo is

Three layers, in descending order of how often you will want them:

| # | Layer | Path | What it is |
|---|---|---|---|
| 1 | **Skill library** | `skills/` | 553 unique skills pulled from 8 local agent CLIs, deduplicated |
| 2 | **Agent brain** | `brain/` | An Obsidian vault: the operating doctrine and the per-project record |
| 3 | **Playbooks** | `*.md` at root | Cybersecurity, AI-development and strategy reference material, plus the original installer scripts |

The skill library is the bulk of it. The brain is the small, high-value part — read
[`brain/Ai Agent Brain/00-Agent-Brain-Index.md`](./brain/Ai%20Agent%20Brain/00-Agent-Brain-Index.md)
first if you are only reading one file.

## Layout

```
skills/<cli>/<skill>/         553 skills — SKILL.md + references/, templates/,
                              scripts/, assets/ (the full folder, not just the file)
SKILLS-INDEX.md               every skill with its description and cross-CLI aliases
_aliases.json                 which other CLIs carry the same skill

brain/Ai Agent Brain/
├── 00-Agent-Brain-Index.md   vault entry point — start here
├── System/                   operating doctrine: Astra OS, DeepSeek 4.1 spec,
│                             Writing Voice, Anti-Slop-Prose, Code-Quality-Bar,
│                             Ponytail, Award-Winning-Design, GitHub-Skills, Sources
├── Skills/                   distilled lessons from real builds + per-area hubs
├── Projects/                 per-project records: Crestorflow, DocCare/EndoCare, Quivane
├── Agents/                   agent definitions
└── Chats/                    saved vault conversations
brain/sources/                raw source documents the doctrine was distilled from
                              (kept outside the vault so the Obsidian graph stays clean)

install-all-skills.sh         installs skills from upstream repos via the skills CLI
install.sh                    basic environment setup
cybersecurity-playbook.md     red/blue team reference
ai-development-guide.md       agent frameworks + MCP reference
ai-ecosystem-strategic-report.md
skills-manifest.md            legacy upstream catalogue (see note below)
skills-reference.md           legacy upstream catalogue (see note below)
```

---

## 🧠 Skill Library

**553 unique skills** consolidated from eight agent CLIs. Each skill is stored as a
**folder** — `SKILL.md` plus its `references/`, `templates/`, `scripts/` and `assets/` —
because flattening to bare `SKILL.md` files loses the support material the skills invoke.

| CLI | Skills |
|---|---|
| `hermes` | 303 |
| `claude` | 97 |
| `gstack` | 95 |
| `agents` | 29 |
| `commandcode` | 11 |
| `muse` | 11 |
| `codex` | 6 |
| `cursor` | 2 |
| **Total** | **553** |

555 `SKILL.md` files are present; 2 are nested duplicates inside `gstack` skill folders,
so the distinct-skill count is 553.

**Deduplication.** A skill carried byte-identically by two CLIs is stored once, under the
first CLI that had it. 111 skills were carried by more than one CLI in the source
installations — the *Also in* column in `SKILLS-INDEX.md` and `_aliases.json` record which.
Without merging, the tree would be about 30% larger and full of silent forks that drift.

**Excluded on purpose:** `node_modules`, `.git`, `dist`, build caches, compiled binaries
and media. The `gstack` tree is 1.6 GB on disk and 7.9 MB as published — the 988 MB of
`node_modules` and ~300 MB of compiled binaries are rebuildable from upstream.
Full inventory: **[`SKILLS-INDEX.md`](./SKILLS-INDEX.md)**.

> **Note on `skills-manifest.md` and `skills-reference.md`:** these are the original
> upstream catalogue of a different ~150-skill set. They do **not** describe what is in
> `skills/`. `SKILLS-INDEX.md` is the authoritative index for this repo.

---

## 🧬 Agent Brain

The operating doctrine and the project record — not skills. A standard Obsidian vault
under `brain/`, so it opens directly in Obsidian if you point a vault at that directory.

The `System/` notes are the instruction layer: autonomy and permission rules, prose
doctrine, the code-quality bar, the design bar, and the reference operating
specifications (the Astra line, distilled from Codex/GPT-6 prompts and translated to
Hermes tools, and the operator-supplied DeepSeek 4.1 specification).

`Skills/` holds lessons written from real builds rather than summaries — the ones worth
reading before debugging in that area. `Projects/` holds per-project records with
verified infrastructure facts and open questions.

> ⚠️ **This vault names real client engagements and carries business detail** —
> `Projects/` documents DocCare/EndoCare and Quivane, including remediation notes and
> account identifiers. It is published here **deliberately, by the owner's decision**, in
> a public repository. Do not assume it is scrubbed.

---

## 🚀 Quick Start

No installer is required to *read* any of this — the skills are plain markdown and the
brain is a plain vault.

```bash
git clone https://github.com/drajeevreddy/ai-company.git ~/ai-company
cd ~/ai-company
```

Read the brain:

```bash
$EDITOR "brain/Ai Agent Brain/00-Agent-Brain-Index.md"
```

Search every skill by description:

```bash
grep -i "kubernetes" SKILLS-INDEX.md
```

### Installing from this repo

`install-all-skills.sh` is the original upstream installer. Be aware of what it does: it
installs the skills CLI and then pulls **~150 skills from third-party upstream
repositories** over the network. It does **not** install the 553 skills in `skills/`.

```bash
bash install-all-skills.sh     # prefer this: read it before you run it
```

The one-liner form exists (`curl -sSL .../install-all-skills.sh | bash`) but reading a
script before running it is better practice, particularly from a repo that ships a
cybersecurity playbook.

To use this repo's own skills, point your agent at the folders directly — most CLIs accept
a skills directory, and each skill is self-contained.

---

## 🔐 Cybersecurity Playbook

Reference material, not an installed toolkit. See
[`cybersecurity-playbook.md`](./cybersecurity-playbook.md).

| Topic | Covered |
|---|---|
| Recon | `nmap`, `amass`, `nuclei` |
| Exploitation | Metasploit |
| Web testing | Burp Suite |
| Autonomous pentesting | PentAGI (Docker) |

Authorized testing only, against systems you own or have written permission to test.

---

## 🤖 AI Agent Frameworks

| Framework | Install | Best for |
|---|---|---|
| LangGraph | `pip install langgraph` | Complex stateful workflows |
| CrewAI | `pip install crewai` | Multi-agent teams |
| AutoGen | `pip install pyautogen` | Microsoft ecosystem |
| OpenAI Agents SDK | `pip install openai-agents` | GPT-native agents |

---

## 🔌 MCP Servers

```bash
# Official (Anthropic)
npx @anthropic-ai/mcp-server-filesystem /path
npx @anthropic-ai/mcp-server-github
npx @anthropic-ai/mcp-server-postgres

# Python
pip install mcp-server-fetch
pip install mcp-server-sqlite
```

Community coverage spans Notion, Slack, Firecrawl, Linear, Sentry and Docker.

---

## 📚 Documentation

| File | Description |
|---|---|
| [`SKILLS-INDEX.md`](./SKILLS-INDEX.md) | **Authoritative** skill index — 553 skills, descriptions, cross-CLI aliases |
| [`brain/Ai Agent Brain/00-Agent-Brain-Index.md`](./brain/Ai%20Agent%20Brain/00-Agent-Brain-Index.md) | Vault entry point |
| [`_aliases.json`](./_aliases.json) | Machine-readable dedup map |
| [`cybersecurity-playbook.md`](./cybersecurity-playbook.md) | Red/blue team reference |
| [`ai-development-guide.md`](./ai-development-guide.md) | Agent frameworks and MCP |
| [`ai-ecosystem-strategic-report.md`](./ai-ecosystem-strategic-report.md) | Industry analysis |
| [`skills-manifest.md`](./skills-manifest.md) · [`skills-reference.md`](./skills-reference.md) | Legacy upstream catalogue — superseded by `SKILLS-INDEX.md` |

---

## ⚖️ Provenance and licensing

Worth stating plainly, because this repo mixes work from several sources:

- **The skill library is not all first-party.** It was collected from the local
  installations of eight agent CLIs. `gstack` (95 skills) is Garry Tan's
  AI-engineering workflow kit, MIT-licensed. Other skills originate from public
  collections — Anthropic's skills, community repos, and vendor-published skills. The
  MIT license below covers this repository's own content; individual skills remain under
  their own upstream licenses and attribution belongs to their authors.
- **The agent brain is first-party** — operating doctrine and project records written for
  this workspace. It quotes from upstream system prompts for reference, with provenance
  recorded in `brain/Ai Agent Brain/System/Sources.md`.
- **The playbooks** (`cybersecurity-playbook.md`, `ai-development-guide.md`,
  `ai-ecosystem-strategic-report.md`) came from the upstream `animeprints/ai-company`
  project this repo was originally copied from.
- **Secrets:** the published tree was scanned for credentials and personal identifiers
  before publishing. The owner's phone number and email, found in five skill reference
  files, were redacted. No API keys are present. The `brain/` client-engagement exposure
  noted above is a deliberate owner decision, not an oversight.

---

## 🤝 Contributing

1. Fork the repo.
2. Add a skill as a **folder** under `skills/`, with `SKILL.md` frontmatter carrying at
   least `name` and `description`.
3. Regenerate `SKILLS-INDEX.md` so the index stays truthful.
4. Open a PR.

---

## 📄 License

MIT for this repository's own content. Third-party skills retain their upstream licenses —
see [Provenance and licensing](#️-provenance-and-licensing).

---

## 🔗 Resources

- **Repository**: https://github.com/drajeevreddy/ai-company
- **Upstream origin of the playbooks**: https://github.com/animeprints/ai-company
- **gstack** (95 of the skills): https://github.com/garrytan/gstack
- **Skills registry**: https://skills.sh
- **MCP registry**: https://mcpindex.net
- **LangChain**: https://python.langchain.com
- **CrewAI**: https://docs.crewai.com
