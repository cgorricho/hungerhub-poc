#!/bin/bash
set -euo pipefail

# STEP 2C DEBUG: CLI_ARGS with --server.port using integer conversion
echo "🔍 STEP 2C: Testing --server.port with INTEGER conversion (no quotes)"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📁 Working from: $(pwd)"

# Basic environment setup
export PROJECT_ROOT="$SCRIPT_DIR"
export PYTHONPATH="$SCRIPT_DIR:${PYTHONPATH:-}"

# Test port - force integer conversion
PORT=8504
PORT_INT=$((PORT))
echo "🚪 Using port: $PORT_INT (converted from: $PORT)"

# CLI_ARGS with --server.port using space format and integer
CLI_ARGS=(
  run
  "$SCRIPT_DIR/src/dashboard/streamlit/enhanced_app.py"
  --server.port
  $PORT_INT
)

# Show what we're about to execute
echo "🚀 Executing: streamlit ${CLI_ARGS[@]}"
echo "📝 Expected URL: http://localhost:$PORT_INT"
echo "📝 Press Ctrl+C to stop when you see it working (or if it stalls)"
echo ""

# Launch Streamlit
exec streamlit "${CLI_ARGS[@]}"
