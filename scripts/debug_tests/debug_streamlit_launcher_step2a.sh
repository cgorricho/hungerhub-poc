#!/bin/bash
set -euo pipefail

# STEP 2A DEBUG: CLI_ARGS with --server.port using equals format
echo "🔍 STEP 2A: Testing --server.port with EQUALS format (--server.port=\"8502\")"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📁 Working from: $(pwd)"

# Basic environment setup
export PROJECT_ROOT="$SCRIPT_DIR"
export PYTHONPATH="$SCRIPT_DIR:${PYTHONPATH:-}"

# Test port
PORT=8502
echo "🚪 Using port: $PORT"

# CLI_ARGS with --server.port using equals format (current broken approach)
CLI_ARGS=(
  run
  "$SCRIPT_DIR/src/dashboard/streamlit/enhanced_app.py"
  --server.port="$PORT"
)

# Show what we're about to execute
echo "🚀 Executing: streamlit ${CLI_ARGS[@]}"
echo "📝 Expected URL: http://localhost:$PORT"
echo "📝 Press Ctrl+C to stop when you see it working (or if it stalls)"
echo ""

# Launch Streamlit
exec streamlit "${CLI_ARGS[@]}"
