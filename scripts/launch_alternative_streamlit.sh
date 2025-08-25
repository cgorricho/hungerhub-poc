#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$SCRIPT_DIR"

LOG_DIR="$REPO_ROOT/logs"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
LOG_FILE="${LOG_DIR}/streamlit_alternative_${TIMESTAMP}.log"

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Check if virtual environment exists, if not use current Python environment
if [ -f "$REPO_ROOT/venv/bin/activate" ]; then
    echo "Activating local virtual environment..."
    source "$REPO_ROOT/venv/bin/activate"
else
    echo "Using current Python environment ($(which python))"
    echo "Python version: $(python --version)"
fi

# Kill any existing Streamlit process if running the alternative app
pkill -f "streamlit.*alternative_app.py" || true

echo "Starting Alternative (Last Known-Good) Streamlit Application..."
echo "Log file: $LOG_FILE"
echo "Access URL: http://localhost:8501"

echo "======== HungerHub Alternative Streamlit Startup ========"
echo "Started at: $(date)"
echo "Working directory: $REPO_ROOT"
echo "Python version: $(python --version)"
echo "Streamlit version: $(streamlit --version 2>/dev/null || echo 'Not available')"
echo "Log file: $LOG_FILE (for reference)"
echo "========================================================="
echo ""
echo "🚀 Starting Alternative Streamlit Application (foreground mode)..."
echo "📍 Access URL: http://localhost:8501"
echo "⚠️  Press Ctrl+C to stop the application"
echo ""

# Run the alternative version in foreground with tee to log and display
exec streamlit run src/dashboard/streamlit/alternative/alternative_app.py \
  --server.port=8501 --server.headless=true --server.runOnSave=false 2>&1 | tee "$LOG_FILE"

