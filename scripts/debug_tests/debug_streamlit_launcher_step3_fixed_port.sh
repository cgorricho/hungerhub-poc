#!/bin/bash
set -euo pipefail

# STEP 3 DEBUG: Fixed port argument using space format instead of equals
echo "🔍 STEP 3: FIXED port argument (--server.port 8502 instead of --server.port=\"8502\")"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📁 Working from: $(pwd)"

# Basic environment setup
export PROJECT_ROOT="$SCRIPT_DIR"
export PYTHONPATH="$SCRIPT_DIR:${PYTHONPATH:-}"

# EXACT same logic as original script for environment variables
PORT="${STREAMLIT_PORT:-8501}"
ADDRESS="${STREAMLIT_ADDRESS:-127.0.0.1}"

# Validate and normalize port (must be integer)
if ! [[ "$PORT" =~ ^[0-9]+$ ]]; then
  echo "❌ Invalid STREAMLIT_PORT value: '$PORT' (must be an integer)" >&2
  exit 1
fi

# Force integer conversion for Streamlit
PORT_INT=$((PORT))

# Optional: bump port if already in use (same as original)
if command -v lsof >/dev/null 2>&1; then
  if lsof -i TCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
    echo "🔁 Port $PORT in use, switching to 8599"
    PORT=8599
    PORT_INT=$((PORT))  # ← FIX: Update PORT_INT when PORT changes
  fi
fi

echo "🚪 PORT='$PORT' (from env var with default)"
echo "🚪 PORT_INT='$PORT_INT' (integer conversion)"
echo "🏠 ADDRESS='$ADDRESS'"

# FIXED CLI_ARGS - Using SPACE format instead of EQUALS format
CLI_ARGS=(
  run
  "$SCRIPT_DIR/src/dashboard/streamlit/enhanced_app.py"
  --server.port
  "$PORT_INT"
)

# Show what we're about to execute
echo "🚀 Executing: streamlit ${CLI_ARGS[@]}"
echo "📝 Expected URL: http://$ADDRESS:$PORT_INT"
echo "📝 Press Ctrl+C to stop when you see it working"
echo ""

# Launch Streamlit with FIXED format
exec streamlit "${CLI_ARGS[@]}"
