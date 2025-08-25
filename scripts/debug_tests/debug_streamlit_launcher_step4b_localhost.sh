#!/bin/bash
set -euo pipefail

# STEP 4B DEBUG: Test with localhost instead of 127.0.0.1
echo "🔍 STEP 4B: Testing --server.address with 'localhost' instead of '127.0.0.1'"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📁 Working from: $(pwd)"

# Basic environment setup
export PROJECT_ROOT="$SCRIPT_DIR"
export PYTHONPATH="$SCRIPT_DIR:${PYTHONPATH:-}"

# Use localhost instead of 127.0.0.1
PORT="${STREAMLIT_PORT:-8501}"
ADDRESS="localhost"  # CHANGED: Force localhost instead of 127.0.0.1

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
echo "🏠 ADDRESS='$ADDRESS' (using localhost instead of 127.0.0.1)"

# CLI_ARGS with localhost address
CLI_ARGS=(
  run
  "$SCRIPT_DIR/src/dashboard/streamlit/enhanced_app.py"
  --server.port
  "$PORT_INT"
  --server.address
  "$ADDRESS"
)

echo "🚀 Executing: streamlit ${CLI_ARGS[@]}"
echo "📝 Expected URL: http://$ADDRESS:$PORT_INT"
echo ""

exec streamlit "${CLI_ARGS[@]}"
