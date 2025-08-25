#!/bin/bash
set -euo pipefail

# Enable bash tracing when TRACE=1 for deeper diagnostics
if [[ "${TRACE:-}" == "1" ]]; then
  set -x
fi

# HungerHub POC - Streamlit Dashboard Launch Script
echo "🍽️ Starting HungerHub Streamlit Dashboard (enhanced app)..."

# Get script directory (project root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📁 Working from: $(pwd)"

# Activate virtual environment if not already active
if [[ "${VIRTUAL_ENV:-}" == "" ]]; then
  if [[ -f "venv/bin/activate" ]]; then
    echo "⚠️ No virtual environment detected. Activating venv..."
    # shellcheck disable=SC1091
    source venv/bin/activate
  else
    echo "⚠️ venv not found. Continuing without activation."
  fi
fi

# Environment hardening for Streamlit
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
export STREAMLIT_SERVER_HEADLESS=true
# Optional flags: FAST=1 skips heavy visuals; NOCACHE=1 disables streamlit cache
if [[ "${FAST:-0}" == "1" ]]; then export DASH_FAST_STARTUP=1; fi
if [[ "${NOCACHE:-0}" == "1" ]]; then export DISABLE_STREAMLIT_CACHE=1; fi
# Use a clean temporary cache to avoid stale state issues
export STREAMLIT_CACHE_DIR="${TMPDIR:-/tmp}/hungerhub_streamlit_cache"
mkdir -p "$STREAMLIT_CACHE_DIR"

# Choose port (allow override via STREAMLIT_PORT)
PORT="${STREAMLIT_PORT:-8501}"
ADDRESS="${STREAMLIT_ADDRESS:-127.0.0.1}"

# Validate and normalize port (must be integer)
if ! [[ "$PORT" =~ ^[0-9]+$ ]]; then
  echo "❌ Invalid STREAMLIT_PORT value: '$PORT' (must be an integer)" >&2
  exit 1
fi

# Force integer conversion for Streamlit
PORT_INT=$((PORT))

# Optional: bump port if already in use
if command -v lsof >/dev/null 2>&1; then
  if lsof -i TCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
    echo "🔁 Port $PORT in use, switching to 8599"
    PORT=8599
    PORT_INT=$((PORT))  # FIX: Update PORT_INT when PORT changes
  fi
fi

# Basic dependency check
if ! command -v streamlit >/dev/null 2>&1; then
  echo "❌ Streamlit is not installed in the current environment. Try: pip install streamlit"
  exit 1
fi

# Informational banner
echo ""
echo "🌐 Streamlit Dashboard will be available at: http://$ADDRESS:$PORT"
echo "📊 Use Ctrl+C to stop the dashboard"
echo ""

# Launch Streamlit dashboard from project root

# Set project root environment variable for robust pathing in the app
export PROJECT_ROOT="$SCRIPT_DIR"
# Ensure Python can import the 'src' package when running via this launcher
export PYTHONPATH="$SCRIPT_DIR:${PYTHONPATH:-}"
# Logging directory and level for app file-based logging
export LOG_DIR="${LOG_DIR:-$SCRIPT_DIR/logs/streamlit}"
mkdir -p "$LOG_DIR"
# Normalize STREAMLIT_LOG_LEVEL to a valid lowercase value expected by Streamlit
_tmp_lvl="${STREAMLIT_LOG_LEVEL:-${LOG_LEVEL:-info}}"
# shellcheck disable=SC2001
_tmp_lvl_lower=$(echo "$_tmp_lvl" | sed 's/.*/\L&/')
case "$_tmp_lvl_lower" in
  error|warning|info|debug) : ;;
  *) _tmp_lvl_lower="info" ;;
esac
export STREAMLIT_LOG_LEVEL="$_tmp_lvl_lower"

# Diagnostics banner
echo "==== Diagnostics ===="
which python || true
python --version || true
which streamlit || true
streamlit --version || true
echo "PROJECT_ROOT=$PROJECT_ROOT"
printf "PYTHONPATH entry[0]=%s\n" "${PYTHONPATH%%:*}"
echo "STREAMLIT_CACHE_DIR=$STREAMLIT_CACHE_DIR"
echo "STREAMLIT_SERVER_HEADLESS=$STREAMLIT_SERVER_HEADLESS"
echo "STREAMLIT_LOG_LEVEL=$STREAMLIT_LOG_LEVEL"
echo "LOG_DIR=$LOG_DIR"
echo "DASH_FAST_STARTUP=${DASH_FAST_STARTUP:-0} DISABLE_STREAMLIT_CACHE=${DISABLE_STREAMLIT_CACHE:-0}"
echo "====================="

# Compute final logger level (STREAMLIT_DEBUG overrides)
LOGGER_LEVEL="$STREAMLIT_LOG_LEVEL"
if [[ "${STREAMLIT_DEBUG:-}" != "" ]]; then
  LOGGER_LEVEL="debug"
fi

# Assemble CLI options (FIXED: space format, no server.address)
CLI_ARGS=(
  run
  "$SCRIPT_DIR/src/dashboard/streamlit/enhanced_app.py"
  --server.port
  "$PORT_INT"
  --logger.level
  "$LOGGER_LEVEL"
)

# Exec Streamlit with explicit flags
exec streamlit "${CLI_ARGS[@]}"
