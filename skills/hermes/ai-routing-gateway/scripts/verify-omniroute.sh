#!/usr/bin/env bash
# verify-omniroute.sh — Quick health check for OmniRoute
# Usage: ./verify-omniroute.sh [host:port]
# Default: localhost:20128

set -euo pipefail

HOST="${1:-localhost:20128}"
BASE="http://${HOST}"

echo "🔍 Verifying OmniRoute at ${BASE}"

# 1. Dashboard reachable
echo -n "  Dashboard (GET /): "
CODE=$(curl -s -o /dev/null -w "%{http_code}" "${BASE}/" || echo "000")
if [[ "${CODE}" =~ ^[23][0-9]{2}$ ]]; then
  echo "✅ ${CODE}"
else
  echo "❌ ${CODE}"
fi

# 2. MCP endpoint
echo -n "  MCP endpoint (GET /api/mcp/stream): "
CODE=$(curl -s -o /dev/null -w "%{http_code}" "${BASE}/api/mcp/stream" || echo "000")
if [[ "${CODE}" =~ ^[234][0-9]{2}$ ]]; then
  echo "✅ ${CODE} (401 = auth required, OK)"
else
  echo "❌ ${CODE}"
fi

# 3. Models API (requires auth)
echo -n "  Models API (GET /api/v1/models): "
CODE=$(curl -s -o /dev/null -w "%{http_code}" "${BASE}/api/v1/models" || echo "000")
if [[ "${CODE}" =~ ^[24][0-9]{2}$ ]]; then
  echo "✅ ${CODE} (401 = auth required, OK)"
else
  echo "❌ ${CODE}"
fi

# 4. Systemd service status (if running locally)
if command -v systemctl >/dev/null 2>&1; then
  echo -n "  Systemd service (omniroute.service): "
  if systemctl --user is-active omniroute.service >/dev/null 2>&1; then
    echo "✅ active"
  elif systemctl --user list-unit-files | grep -q omniroute.service; then
    echo "⚠️  installed but inactive"
  else
    echo "❌ not installed"
  fi
fi

echo ""
echo "📋 Quick login test (requires admin password):"
echo "  curl -X POST ${BASE}/api/auth/login -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"YOUR_PASSWORD\"}'"