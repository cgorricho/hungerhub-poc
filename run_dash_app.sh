#!/bin/bash

# HungerHub POC - Dash Dashboard Launcher with tmux
# This script runs from /home/tagazureuser and launches the Dash app in a persistent tmux session

PROJECT_DIR="/home/tagazureuser/cgorr/2week_poc_execution/hungerhub_poc"
VENV_PATH="$PROJECT_DIR/venv"
DASH_APP_PATH="$PROJECT_DIR/src/dashboard/dash"
LOG_DIR="$PROJECT_DIR/logs"
SESSION_NAME="hungerhub-dash"

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Timestamp for log files
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="$LOG_DIR/dash_app_$TIMESTAMP.log"

echo "Starting Dash Dashboard in tmux session '$SESSION_NAME'..."
echo "Log file: $LOG_FILE"

# Check if virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    echo "Error: Virtual environment not found at $VENV_PATH"
    exit 1
fi

# Check if tmux session already exists
if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    echo "tmux session '$SESSION_NAME' already exists."
    echo "Attaching to existing session..."
    tmux attach-session -t "$SESSION_NAME"
else
    echo "Creating new tmux session '$SESSION_NAME'..."
    
    # Create a new tmux session with the startup commands
    tmux new-session -d -s "$SESSION_NAME" -c "$PROJECT_DIR"
    
    # Send commands to the tmux session
    tmux send-keys -t "$SESSION_NAME" "echo 'Starting Dash Dashboard...' | tee -a '$LOG_FILE'" Enter
    tmux send-keys -t "$SESSION_NAME" "echo 'Log file: $LOG_FILE' | tee -a '$LOG_FILE'" Enter
    tmux send-keys -t "$SESSION_NAME" "echo 'Activated virtual environment' | tee -a '$LOG_FILE'" Enter
    tmux send-keys -t "$SESSION_NAME" "echo 'Running from project root: $PROJECT_DIR' | tee -a '$LOG_FILE'" Enter
    tmux send-keys -t "$SESSION_NAME" "echo 'Dash app path: $DASH_APP_PATH' | tee -a '$LOG_FILE'" Enter
    
    # Activate virtual environment and run the Dash app
    tmux send-keys -t "$SESSION_NAME" "source '$VENV_PATH/bin/activate'" Enter
    tmux send-keys -t "$SESSION_NAME" "python src/dashboard/dash/app.py 2>&1 | tee -a '$LOG_FILE'" Enter
    
    # Attach to the session
    echo "Attaching to tmux session '$SESSION_NAME'..."
    tmux attach-session -t "$SESSION_NAME"
fi
