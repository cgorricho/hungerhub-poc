#!/bin/bash
set -euo pipefail

# STEP 5 DEBUG: Final version - port + logger.level (NO server.address)
echo "🔍 STEP 5: FINAL version with --server.port and --logger.level (NO --server.address)"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📁 Working from: $(pwd)"

# Basic environment setup
export PROJECT_ROOT="$SCRIPT_DIR"
export PYTHONPATH="$SCRIPT_DIR:${PYTHONPATH:-}"

# EXACT same logic as original script for environment variables
PORT="${STREAMLIT_PORT:-8501}"
ADDRESS="${STREAMLIT_ADDRESS:-127.0.0.1}"  # Defined but not used in CLI_ARGS

# Validate and normalize port
if ! [[ "$PORT" =~ ^[0-9]+$ ]]; then
  echo "❌ Invalid STREAMLIT_PORT value: '$PORT' (must be an integer)" >&2
  exit 1
fi

PORT_INT=$((PORT))

# Optional: bump port if already in use (same as original)
if command -v lsof >/dev/null 2>&1; then
  if lsof -i TCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
    echo "🔁 Port $PORT in use, switching to 8599"
    PORT=8599
    PORT_INT=$((PORT))
  fi
fi

# Logger level logic (same as original)
_tmp_lvl="${STREAMLIT_LOG_LEVEL:-${LOG_LEVEL:-info}}"
_tmp_lvl_lower=$(echo "$_tmp_lvl" | sed 's/.*/\L&/')
case "$_tmp_lvl_lower" in
  error|warning|info|debug) : ;;
  *) _tmp_lvl_lower="info" ;;
esac

LOGGER_LEVEL="$_tmp_lvl_lower"
if [[ "${STREAMLIT_DEBUG:-}" != "" ]]; then
  LOGGER_LEVEL="debug"
fi

echo "🚪 PORT_INT='$PORT_INT'"
echo "📝 LOGGER_LEVEL='$LOGGER_LEVEL'"
echo "🏠 ADDRESS='$ADDRESS' (defined but NOT passed to Streamlit - using default)"

# FINAL CLI_ARGS - Using SPACE format, NO server.address
CLI_ARGS=(
  run
  "$SCRIPT_DIR/src/dashboard/streamlit/enhanced_app.py"
  --server.port
  "$PORT_INT"
  --logger.level
  "$LOGGER_LEVEL"
)

# Show what we're about to execute
echo "🚀 Executing: streamlit ${CLI_ARGS[@]}"
echo "📝 Expected: Should work without stalling"
echo ""

# Launch Streamlit with FINAL working format
exec streamlit "${CLI_ARGS[@]}"
