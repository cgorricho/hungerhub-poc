#!/bin/bash

# HungerHub POC - Dashboard Log Monitor
echo "🔍 HungerHub Dashboard Log Monitor"
echo "=" * 40

# Find the most recent log files
LATEST_MAIN_LOG=$(ls -t logs/dashboard_*.log 2>/dev/null | head -1)
LATEST_ERROR_LOG=$(ls -t logs/dashboard_errors_*.log 2>/dev/null | head -1)
LATEST_CONSOLE_LOG=$(ls -t logs/console_*.log 2>/dev/null | head -1)

if [[ -z "$LATEST_ERROR_LOG" && -z "$LATEST_MAIN_LOG" && -z "$LATEST_CONSOLE_LOG" ]]; then
    echo "❌ No dashboard log files found. Start the dashboard first."
    exit 1
fi

echo "📝 Monitoring log files:"
[[ -n "$LATEST_MAIN_LOG" ]] && echo "   Main: $LATEST_MAIN_LOG"
[[ -n "$LATEST_ERROR_LOG" ]] && echo "   Errors: $LATEST_ERROR_LOG"  
[[ -n "$LATEST_CONSOLE_LOG" ]] && echo "   Console: $LATEST_CONSOLE_LOG"
echo ""

# Function to show recent errors
show_recent_errors() {
    echo "🚨 Recent Errors (last 20 lines):"
    echo "-" * 35
    if [[ -n "$LATEST_ERROR_LOG" && -f "$LATEST_ERROR_LOG" ]]; then
        tail -20 "$LATEST_ERROR_LOG"
    else
        echo "No error log file found or file is empty."
    fi
    echo ""
}

# Function to show live error monitoring  
monitor_errors() {
    echo "👀 Live Error Monitoring (Ctrl+C to stop):"
    echo "-" * 40
    if [[ -n "$LATEST_ERROR_LOG" && -f "$LATEST_ERROR_LOG" ]]; then
        tail -f "$LATEST_ERROR_LOG"
    else
        echo "No error log file to monitor."
    fi
}

# Function to show all recent logs
show_recent_all() {
    echo "📋 Recent All Logs (last 30 lines):"
    echo "-" * 35
    if [[ -n "$LATEST_MAIN_LOG" && -f "$LATEST_MAIN_LOG" ]]; then
        tail -30 "$LATEST_MAIN_LOG"
    else
        echo "No main log file found."
    fi
    echo ""
}

# Main menu
case "${1:-menu}" in
    "errors")
        show_recent_errors
        ;;
    "monitor")
        monitor_errors
        ;;
    "all")
        show_recent_all
        ;;
    "menu"|*)
        echo "Choose an option:"
        echo "1) Show recent errors"
        echo "2) Monitor errors live"  
        echo "3) Show all recent logs"
        echo ""
        read -p "Enter choice (1-3): " choice
        
        case $choice in
            1) show_recent_errors ;;
            2) monitor_errors ;;
            3) show_recent_all ;;
            *) echo "Invalid choice" ;;
        esac
        ;;
esac
