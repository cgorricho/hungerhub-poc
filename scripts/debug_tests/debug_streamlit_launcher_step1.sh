#!/bin/bash
set -euo pipefail

# STEP 1 DEBUG: CLI_ARGS without any arguments
echo "🔍 STEP 1: Testing Streamlit launch with NO additional arguments"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📁 Working from: $(pwd)"

# Basic environment setup
export PROJECT_ROOT="$SCRIPT_DIR"
export PYTHONPATH="$SCRIPT_DIR:${PYTHONPATH:-}"

# Simple CLI_ARGS - just the minimum required
CLI_ARGS=(
  run
  "$SCRIPT_DIR/src/dashboard/streamlit/enhanced_app.py"
)

# Show what we're about to execute
echo "🚀 Executing: streamlit ${CLI_ARGS[@]}"
echo "📝 Press Ctrl+C to stop when you see it working"
echo ""

# Launch Streamlit with minimal args
exec streamlit "${CLI_ARGS[@]}"
