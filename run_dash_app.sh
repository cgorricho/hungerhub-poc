#!/bin/bash
set -euo pipefail

# Enable bash tracing when TRACE=1 for deeper diagnostics
if [[ "${TRACE:-}" == "1" ]]; then
  set -x
fi

# HungerHub POC - Dash Dashboard Launch Script
echo "📊 Starting HungerHub Dash Dashboard (enhanced app)..."

# Get script directory (project root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📁 Working from: $(pwd)"

# Activate virtual environment if not already active
if [[ "${VIRTUAL_ENV:-}" == "" ]]; then
  if [[ -f "venv/bin/activate" ]]; then
    echo "🐍 Activating virtual environment..."
    source venv/bin/activate
  elif [[ -f "../../../venvconda/bin/activate" ]]; then
    echo "🐍 Using conda virtual environment..."
    source ../../../venvconda/bin/activate
  else
    echo "⚠️ No virtual environment detected. Trying to use system Python with dependencies..."
  fi
fi

# Optional: load env vars if present
if [ -f "config/.env" ]; then
  set -a
  # shellcheck disable=SC1091
  . config/.env
  set +a
fi

# Set up environment variables
export PROJECT_ROOT="$SCRIPT_DIR"
export PYTHONPATH="$PROJECT_ROOT:${PYTHONPATH:-}"
export LOG_LEVEL="INFO"

echo "🌐 Dash Dashboard will be available at: http://127.0.0.1:8050"
echo "📊 Use Ctrl+C to stop the dashboard"

echo ""
echo "==== Diagnostics ===="
which python
python --version
python -c "import dash; print('Dash version:', dash.__version__)" 2>/dev/null || echo "Dash not installed"
echo "PROJECT_ROOT=$PROJECT_ROOT"
echo "PYTHONPATH entry[0]=$(echo "$PYTHONPATH" | cut -d: -f1)"
echo "LOG_LEVEL=$LOG_LEVEL"
echo "====================="
echo ""

# Run Dash app
echo "🚀 Launching Dash application..."
python -m src.dashboard.dash.enhanced_app
