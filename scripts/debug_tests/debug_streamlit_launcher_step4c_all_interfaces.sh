#!/bin/bash
set -euo pipefail

# STEP 4C DEBUG: Test with 0.0.0.0 (bind to all interfaces)
echo "🔍 STEP 4C: Testing --server.address with '0.0.0.0' (all interfaces)"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📁 Working from: $(pwd)"

# Basic environment setup
export PROJECT_ROOT="$SCRIPT_DIR"
export PYTHONPATH="$SCRIPT_DIR:${PYTHONPATH:-}"

# Use 0.0.0.0 to bind to all interfaces
PORT="${STREAMLIT_PORT:-8501}"
ADDRESS="0.0.0.0"  # CHANGED: Bind to all interfaces

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
echo "🏠 ADDRESS='$ADDRESS' (binding to all interfaces)"

# CLI_ARGS with 0.0.0.0 address
CLI_ARGS=(
  run
  "$SCRIPT_DIR/src/dashboard/streamlit/enhanced_app.py"
  --server.port
  "$PORT_INT"
  --server.address
  "$ADDRESS"
)

echo "🚀 Executing: streamlit ${CLI_ARGS[@]}"
echo "📝 Expected URL: http://localhost:$PORT_INT (accessible via any interface)"
echo ""

exec streamlit "${CLI_ARGS[@]}"
