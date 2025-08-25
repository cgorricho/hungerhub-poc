#!/bin/bash

# HungerHub POC - Plotly Dash Dashboard Launch Script with Enhanced VEnv Management
echo "🍽️ Starting HungerHub POC Dashboard..."
echo "📋 Original POC Specification: Oracle → Python → Plotly Dash"

# Create timestamp for log files
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Ensure logs directory exists
mkdir -p logs

# Define log files
TERMINAL_LOG="logs/terminal_output_${TIMESTAMP}.log"
DASHBOARD_LOG="logs/dashboard_process_${TIMESTAMP}.log"

# Function to log with timestamp
log_with_timestamp() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$TERMINAL_LOG"
}

# Start logging
log_with_timestamp "🚀 Dashboard launch initiated"
log_with_timestamp "📝 Terminal output will be saved to: $TERMINAL_LOG"

# Virtual Environment Management
EXPECTED_VENV_PATH="$(pwd)/venv"
CURRENT_VENV_PATH="$VIRTUAL_ENV"

log_with_timestamp "🐍 Checking Python virtual environment..."
log_with_timestamp "📍 Expected venv: $EXPECTED_VENV_PATH"
log_with_timestamp "📍 Current venv: ${CURRENT_VENV_PATH:-'None'}"

# Function to activate virtual environment
activate_venv() {
    log_with_timestamp "🔧 Activating virtual environment..."
    
    # Source the activation script
    if source "$EXPECTED_VENV_PATH/bin/activate"; then
        # Verify activation worked by checking VIRTUAL_ENV
        if [[ "$VIRTUAL_ENV" == "$EXPECTED_VENV_PATH" ]]; then
            log_with_timestamp "✅ Successfully activated: $VIRTUAL_ENV"
            return 0
        else
            log_with_timestamp "❌ Activation failed - VIRTUAL_ENV not set correctly"
            return 1
        fi
    else
        log_with_timestamp "❌ Failed to source activation script"
        return 1
    fi
}

# Check if we need to activate/switch virtual environment
if [[ "$CURRENT_VENV_PATH" != "$EXPECTED_VENV_PATH" ]]; then
    if [[ -n "$CURRENT_VENV_PATH" ]]; then
        log_with_timestamp "⚠️ Different virtual environment active. Deactivating current..."
        deactivate 2>/dev/null || true
    fi
    
    if [[ -d "$EXPECTED_VENV_PATH" && -f "$EXPECTED_VENV_PATH/bin/activate" ]]; then
        if activate_venv; then
            log_with_timestamp "✅ Virtual environment setup complete"
        else
            log_with_timestamp "❌ Virtual environment activation failed"
            exit 1
        fi
    else
        log_with_timestamp "❌ Virtual environment not found or invalid: $EXPECTED_VENV_PATH"
        log_with_timestamp "🔧 Creating new virtual environment..."
        
        if python3 -m venv "$EXPECTED_VENV_PATH"; then
            log_with_timestamp "✅ Virtual environment created"
            if activate_venv; then
                log_with_timestamp "✅ New virtual environment activated"
            else
                log_with_timestamp "❌ Failed to activate new virtual environment"
                exit 1
            fi
        else
            log_with_timestamp "❌ Failed to create virtual environment"
            exit 1
        fi
        
        if [[ -f "requirements.txt" ]]; then
            log_with_timestamp "📦 Installing requirements..."
            if pip install -r requirements.txt 2>&1 | tee -a "$TERMINAL_LOG"; then
                log_with_timestamp "✅ Requirements installed"
            else
                log_with_timestamp "❌ Failed to install requirements"
                exit 1
            fi
        fi
    fi
else
    log_with_timestamp "✅ Correct virtual environment already active: $VIRTUAL_ENV"
fi

# Verify Python environment
log_with_timestamp "🔍 Verifying Python environment..."
PYTHON_PATH=$(which python)
PYTHON_VERSION=$(python --version 2>&1)
PIP_VERSION=$(pip --version 2>&1)
log_with_timestamp "🐍 Python path: $PYTHON_PATH"
log_with_timestamp "🐍 Python: $PYTHON_VERSION"
log_with_timestamp "📦 Pip: $PIP_VERSION"

# Check for required packages
log_with_timestamp "📋 Checking required packages..."
REQUIRED_PACKAGES=("dash" "plotly" "pandas" "cx_Oracle")
MISSING_PACKAGES=()

for package in "${REQUIRED_PACKAGES[@]}"; do
    if python -c "import $package" 2>/dev/null; then
        VERSION=$(python -c "import $package; print(getattr($package, '__version__', 'unknown'))" 2>/dev/null)
        log_with_timestamp "✅ $package ($VERSION)"
    else
        log_with_timestamp "❌ Missing: $package"
        MISSING_PACKAGES+=("$package")
    fi
done

# Install missing packages if any
if [[ ${#MISSING_PACKAGES[@]} -gt 0 ]]; then
    log_with_timestamp "🔧 Installing missing packages: ${MISSING_PACKAGES[*]}"
    if pip install "${MISSING_PACKAGES[@]}" 2>&1 | tee -a "$TERMINAL_LOG"; then
        log_with_timestamp "✅ Missing packages installed"
    else
        log_with_timestamp "❌ Failed to install missing packages"
        exit 1
    fi
fi

# Check if real data exists
if [ ! -f "data/processed/unified_real/donations.csv" ] || [ ! -f "data/processed/unified_real/organizations.csv" ]; then
    log_with_timestamp "❌ Real Oracle data files not found. Running data extraction..."
    
    if python src/data_extraction/real_data_extractor.py 2>&1 | tee -a "$TERMINAL_LOG"; then
        log_with_timestamp "✅ Data extraction completed"
    else
        log_with_timestamp "❌ Data extraction failed. Check terminal log for details."
        exit 1
    fi
    
    if python src/data_extraction/create_unified_real_data.py 2>&1 | tee -a "$TERMINAL_LOG"; then
        log_with_timestamp "✅ Data unification completed"
    else
        log_with_timestamp "❌ Data unification failed. Check terminal log for details."
        exit 1
    fi
else
    log_with_timestamp "✅ Real Oracle data files found"
fi

# Check dashboard app exists
if [ ! -f "src/dashboard/app.py" ]; then
    log_with_timestamp "❌ Dashboard app not found: src/dashboard/app.py"
    exit 1
fi

log_with_timestamp "🎯 3-Page Dashboard: Executive Summary | Donation Analytics | Agency Operations"
log_with_timestamp "🌐 Dashboard will be available at: http://localhost:8050"
log_with_timestamp "📊 Using real Oracle data with 7,500+ records"
log_with_timestamp "📝 Comprehensive logging enabled:"
log_with_timestamp "   - Terminal output: $TERMINAL_LOG"
log_with_timestamp "   - Dashboard logs: logs/dashboard_${TIMESTAMP}.log"
log_with_timestamp "   - Error logs: logs/dashboard_errors_${TIMESTAMP}.log"
log_with_timestamp "   - Process logs: $DASHBOARD_LOG"
log_with_timestamp "⚠️ Use Ctrl+C to stop the dashboard"

# Create a function to handle cleanup on exit
cleanup() {
    log_with_timestamp "🛑 Dashboard shutdown signal received"
    log_with_timestamp "📝 All log files saved in logs/ directory"
    log_with_timestamp "🔚 Dashboard process terminated"
    exit 0
}

# Trap Ctrl+C to run cleanup
trap cleanup SIGINT SIGTERM

log_with_timestamp "🚀 Starting dashboard server..."

# Launch Dash dashboard with ALL output captured
# This captures both stdout and stderr from the Python process
exec > >(tee -a "$DASHBOARD_LOG")
exec 2> >(tee -a "$DASHBOARD_LOG" >&2)

# Log the start time
echo "[$(date '+%Y-%m-%d %H:%M:%S')] === DASHBOARD PROCESS START ===" >> "$DASHBOARD_LOG"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Command: python src/dashboard/app.py" >> "$DASHBOARD_LOG"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Virtual Environment: $VIRTUAL_ENV" >> "$DASHBOARD_LOG"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Python Path: $(which python)" >> "$DASHBOARD_LOG"

# Start the dashboard - all output will now go to both console and log file
python src/dashboard/app.py

# If we reach here, the dashboard exited
echo "[$(date '+%Y-%m-%d %H:%M:%S')] === DASHBOARD PROCESS END ===" >> "$DASHBOARD_LOG"
log_with_timestamp "🔚 Dashboard process completed normally"
