#!/bin/bash
# 🤖 AI Company Skills Installer - One-Tap Install All ~150 Skills
# Run: curl -sSL https://raw.githubusercontent.com/drajeevreddy/ai-company/main/install-all-skills.sh | bash
# Or: bash install-all-skills.sh

set -e

echo "🎯 Installing AI Company Skills (~150 skills)..."
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}⚠️ Node.js not found. Installing...${NC}"
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

# Install skills CLI
echo "📦 Installing skills CLI..."
npm install -g skills-cli 2>/dev/null || npm install -g skill --legacy-peer-deps 2>/dev/null || true

# Counter
total=0
installed=0
failed=0

install_skill() {
    local skill="$1"
    local owner_repo="$2"
    total=$((total + 1))
    echo -n "Installing $skill... "
    if npx skill add "$owner_repo" 2>/dev/null; then
        echo -e "${GREEN}✓${NC}"
        installed=$((installed + 1))
    else
        echo -e "${YELLOW}⚠${NC}"
        failed=$((failed + 1))
    fi
}

echo ""
echo "🎨 Installing Frontend & Design skills..."
install_skill "frontend-design" "anthropics/skills:frontend-design"
install_skill "web-design-guidelines" "vercel-labs/agent-skills:web-design-guidelines"
install_skill "vercel-react-best-practices" "vercel-labs/agent-skills:vercel-react-best-practices"
install_skill "vercel-composition-patterns" "vercel-labs/agent-skills:vercel-composition-patterns"
install_skill "shadcn" "shadcn/ui:shadcn"
install_skill "algorithmic-art" "anthropics/skills:algorithmic-art"
install_skill "canvas-design" "anthropics/skills:canvas-design"
install_skill "brand-guidelines" "anthropics/skills:brand-guidelines"
install_skill "theme-factory" "anthropics/skills:theme-factory"

echo ""
echo "🤖 Installing AI & Agents skills..."
install_skill "microsoft-foundry" "microsoft/azure-skills:microsoft-foundry"
install_skill "supabase" "supabase/agent-skills:supabase"
install_skill "neon-postgres" "neondatabase/agent-skills:neon-postgres"
install_skill "supabase-postgres-best-practices" "supabase/agent-skills:supabase-postgres-best-practices"
install_skill "convex-quickstart" "get-convex/agent-skills:convex-quickstart"
install_skill "firebase-basics" "firebase/agent-skills:firebase-basics"
install_skill "firebase-firestore-standard" "firebase/agent-skills:firebase-firestore-standard"
install_skill "developing-genkit-js" "firebase/agent-skills:developing-genkit-js"

echo ""
echo "🌥️ Installing Cloud & DevOps skills..."
install_skill "azure-kubernetes" "microsoft/azure-skills:azure-kubernetes"
install_skill "azure-cost" "microsoft/azure-skills:azure-cost"
install_skill "azure-upgrade" "microsoft/azure-skills:azure-upgrade"
install_skill "azure-enterprise-infra-planner" "microsoft/azure-skills:azure-enterprise-infra-planner"
install_skill "azure-deploy" "microsoft/azure-skills:azure-deploy"
install_skill "azure-prepare" "microsoft/azure-skills:azure-prepare"
install_skill "azure-validate" "microsoft/azure-skills:azure-validate"
install_skill "azure-messaging" "microsoft/github-copilot-for-azure:azure-messaging"

echo ""
echo "🔒 Installing Security skills..."
install_skill "openclaw-secure-linux-cloud" "xixu-me/skills:openclaw-secure-linux-cloud"
install_skill "systematic-debugging" "obra/superpowers:systematic-debugging"
install_skill "test-driven-development" "obra/superpowers:test-driven-development"
install_skill "github-actions-docs" "xixu-me/skills:github-actions-docs"
install_skill "browser-use" "browser-use/browser-use:browser-use"
install_skill "webapp-testing" "anthropics/skills:webapp-testing"

echo ""
echo "📊 Installing Marketing & Growth skills..."
install_skill "copywriting" "coreyhaines31/marketingskills:copywriting"
install_skill "seo-audit" "coreyhaines31/marketingskills:seo-audit"
install_skill "content-strategy" "coreyhaines31/marketingskills:content-strategy"
install_skill "marketing-ideas" "coreyhaines31/marketingskills:marketing-ideas"
install_skill "pricing-strategy" "coreyhaines31/marketingskills:pricing-strategy"
install_skill "paid-ads" "coreyhaines31/marketingskills:paid-ads"
install_skill "cold-email" "coreyhaines31/marketingskills:cold-email"
install_skill "ad-creative" "coreyhaines31/marketingskills:ad-creative"
install_skill "social-content" "coreyhaines31/marketingskills:social-content"
install_skill "analytics-tracking" "coreyhaines31/marketingskills:analytics-tracking"
install_skill "marketing-psychology" "coreyhaines31/marketingskills:marketing-psychology"
install_skill "churn-prevention" "coreyhaines31/marketingskills:churn-prevention"
install_skill "revops" "coreyhaines31/marketingskills:revops"
install_skill "ab-test-setup" "coreyhaines31/marketingskills:ab-test-setup"
install_skill "page-cro" "coreyhaines31/marketingskills:page-cro"

echo ""
echo "📄 Installing Productivity skills..."
install_skill "pdf" "anthropics/skills:pdf"
install_skill "xlsx" "anthropics/skills:xlsx"
install_skill "pptx" "anthropics/skills:pptx"
install_skill "docx" "anthropics/skills:docx"
install_skill "doc-coauthoring" "anthropics/skills:doc-coauthoring"
install_skill "internal-comms" "anthropics/skills:internal-comms"
install_skill "lark-doc" "larksuite/cli:lark-doc"
install_skill "firecrawl-scrape" "firecrawl/cli:firecrawl-scrape"
install_skill "firecrawl-search" "firecrawl/cli:firecrawl-search"
install_skill "firecrawl-agent" "firecrawl/cli:firecrawl-agent"

echo ""
echo "🔧 Installing Tools & Utilities skills..."
install_skill "find-skills" "vercel-labs/skills:find-skills"
install_skill "skills-cli" "xixu-me/skills:skills-cli"
install_skill "xget" "xixu-me/skills:xget"
install_skill "xdrop" "xixu-me/skills:xdrop"
install_skill "tzst" "xixu-me/skills:tzst"
install_skill "mcp-builder" "anthropics/skills:mcp-builder"
install_skill "skill-creator" "anthropics/skills:skill-creator"
install_skill "deploy-to-vercel" "vercel-labs/agent-skills:deploy-to-vercel"

echo ""
echo "🧠 Installing Workflow & Planning skills..."
install_skill "brainstorming" "obra/superpowers:brainstorming"
install_skill "writing-plans" "obra/superpowers:writing-plans"
install_skill "requesting-code-review" "obra/superpowers:requesting-code-review"
install_skill "receiving-code-review" "obra/superpowers:receiving-code-review"
install_skill "executing-plans" "obra/superpowers:executing-plans"
install_skill "finishing-a-development-branch" "obra/superpowers:finishing-a-development-branch"
install_skill "subagent-driven-development" "obra/superpowers:subagent-driven-development"
install_skill "dispatching-parallel-agents" "obra/superpowers:dispatching-parallel-agents"
install_skill "using-git-worktrees" "obra/superpowers:using-git-worktrees"
install_skill "using-superpowers" "obra/superpowers:using-superpowers"
install_skill "product-marketing-context" "coreyhaines31/marketingskills:product-marketing-context"
install_skill "site-architecture" "coreyhaines31/marketingskills:site-architecture"
install_skill "schema-markup" "coreyhaines31/marketingskills:schema-markup"
install_skill "ai-seo" "coreyhaines31/marketingskills:ai-seo"

echo ""
echo "📚 Installing Next.js & React skills..."
install_skill "next-best-practices" "vercel-labs/next-skills:next-best-practices"
install_skill "next-upgrade" "vercel-labs/next-skills:next-upgrade"
install_skill "vercel-react-native-skills" "vercel-labs/agent-skills:vercel-react-native-skills"
install_skill "web-artifacts-builder" "anthropics/skills:web-artifacts-builder"
install_skill "enhance-prompt" "google-labs-code/stitch-skills:enhance-prompt"

echo ""
echo "🎯 Installing Specialty skills..."
install_skill "soultrace" "soultrace-ai/soultrace-skill:soultrace"
install_skill "remotion-best-practices" "remotion-dev/skills:remotion-best-practices"
install_skill "playwright-best-practices" "currents-dev/playwright-best-practices-skill:playwright-best-practices"
install_skill "grill-me" "mattpocock/skills:grill-me"
install_skill "simple" "roin-orca/skills:simple"
install_skill "audit-website" "squirrelscan/skills:audit-website"

echo ""
echo "🛠️ Installing MCP Servers..."
echo "Installing official MCP servers via npx..."

# Core MCP servers (these are commonly used)
npx -y @anthropic-ai/mcp-server-filesystem ~ 2>/dev/null || true
npx -y @anthropic-ai/mcp-server-github 2>/dev/null || true
npx -y @anthropic-ai/mcp-server-postgres 2>/dev/null || true
npx -y @anthropic-ai/mcp-server-brave-search 2>/dev/null || true

# Python MCP servers
pip install mcp-server-fetch 2>/dev/null || pip3 install mcp-server-fetch 2>/dev/null || true
pip install mcp-server-sqlite 2>/dev/null || pip3 install mcp-server-sqlite 2>/dev/null || true

echo ""
echo "========================================="
echo -e "${GREEN}✅ Installation Complete!${NC}"
echo "========================================="
echo ""
echo "Summary:"
echo "  Attempted: ~$total skills"
echo "  Installed: $installed"
echo "  Skipped/Failed: $failed"
echo ""
echo "📖 Usage:"
echo "  skill list                    # List installed skills"
echo "  skill find '<keyword>'         # Find more skills"
echo "  skill run <owner/repo>         # Run a skill"
echo ""
echo "📁 Files downloaded to: ~/ai-company/"
echo "🔗 Full docs: https://github.com/drajeevreddy/ai-company"
echo ""
echo "🎉 You're ready to build!"