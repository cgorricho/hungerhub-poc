#!/bin/bash
set -euo pipefail

# STEP 4A DEBUG: Confirm --server.address is the problem by removing it
echo "🔍 STEP 4A: Testing WITHOUT --server.address (should work like Step 3)"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📁 Working from: $(pwd)"

# Basic environment setup
export PROJECT_ROOT="$SCRIPT_DIR"
export PYTHONPATH="$SCRIPT_DIR:${PYTHONPATH:-}"

# Same logic as Step 4 but NO ADDRESS in CLI_ARGS
PORT="${STREAMLIT_PORT:-8501}"
ADDRESS="${STREAMLIT_ADDRESS:-127.0.0.1}"

# Validate and normalize port
if ! [[ "$PORT" =~ ^[0-9]+$ ]]; then
  echo "❌ Invalid STREAMLIT_PORT value: '$PORT' (must be an integer)" >&2
  exit 1
fi

PORT_INT=$((PORT))

# Optional: bump port if already in use
if command -v lsof >/dev/null 2>&1; then
  if lsof -i TCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
    echo "🔁 Port $PORT in use, switching to 8599"
    PORT=8599
    PORT_INT=$((PORT))
  fi
fi

echo "🚪 PORT_INT='$PORT_INT'"
echo "🏠 ADDRESS='$ADDRESS' (defined but NOT passed to Streamlit)"

# CLI_ARGS WITHOUT --server.address (should work)
CLI_ARGS=(
  run
  "$SCRIPT_DIR/src/dashboard/streamlit/enhanced_app.py"
  --server.port
  "$PORT_INT"
)

echo "🚀 Executing: streamlit ${CLI_ARGS[@]}"
echo "📝 Expected: Should work (no address parameter)"
echo ""

exec streamlit "${CLI_ARGS[@]}"
