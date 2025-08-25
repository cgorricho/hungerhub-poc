#!/bin/bash

# HungerHub POC - Terminal Log Inspector
echo "🔍 HungerHub Terminal Log Inspector"
echo "=" * 40

# Find the most recent log files
LATEST_TERMINAL=$(ls -t logs/terminal_output_*.log 2>/dev/null | head -1)
LATEST_DASHBOARD=$(ls -t logs/dashboard_process_*.log 2>/dev/null | head -1)

if [[ -z "$LATEST_TERMINAL" && -z "$LATEST_DASHBOARD" ]]; then
    echo "❌ No terminal log files found. Start the dashboard first with ./launch_dash_dashboard.sh"
    exit 1
fi

echo "📝 Available log files:"
[[ -n "$LATEST_TERMINAL" ]] && echo "   Terminal: $LATEST_TERMINAL"
[[ -n "$LATEST_DASHBOARD" ]] && echo "   Dashboard Process: $LATEST_DASHBOARD"
echo ""

# Function to show terminal log
show_terminal_log() {
    if [[ -n "$LATEST_TERMINAL" && -f "$LATEST_TERMINAL" ]]; then
        echo "📋 Terminal Output Log (last 50 lines):"
        echo "-" * 50
        tail -50 "$LATEST_TERMINAL"
        echo ""
        echo "📊 Full file: $LATEST_TERMINAL ($(wc -l < "$LATEST_TERMINAL") lines)"
    else
        echo "❌ No terminal log file found."
    fi
}

# Function to show dashboard process log
show_dashboard_log() {
    if [[ -n "$LATEST_DASHBOARD" && -f "$LATEST_DASHBOARD" ]]; then
        echo "🖥️ Dashboard Process Log (last 50 lines):"
        echo "-" * 50
        tail -50 "$LATEST_DASHBOARD"
        echo ""
        echo "📊 Full file: $LATEST_DASHBOARD ($(wc -l < "$LATEST_DASHBOARD") lines)"
    else
        echo "❌ No dashboard process log file found."
    fi
}

# Function to search for errors
search_errors() {
    echo "🚨 Searching for errors in logs:"
    echo "-" * 30
    
    if [[ -n "$LATEST_TERMINAL" && -f "$LATEST_TERMINAL" ]]; then
        echo "📋 Terminal log errors:"
        grep -i "error\|exception\|traceback\|failed" "$LATEST_TERMINAL" | tail -10
        echo ""
    fi
    
    if [[ -n "$LATEST_DASHBOARD" && -f "$LATEST_DASHBOARD" ]]; then
        echo "🖥️ Dashboard process errors:"
        grep -i "error\|exception\|traceback\|failed" "$LATEST_DASHBOARD" | tail -10
        echo ""
    fi
}

# Function to monitor live
monitor_live() {
    echo "👀 Live Log Monitoring (Ctrl+C to stop):"
    echo "-" * 40
    
    if [[ -n "$LATEST_DASHBOARD" && -f "$LATEST_DASHBOARD" ]]; then
        tail -f "$LATEST_DASHBOARD"
    elif [[ -n "$LATEST_TERMINAL" && -f "$LATEST_TERMINAL" ]]; then
        tail -f "$LATEST_TERMINAL"
    else
        echo "❌ No log files to monitor."
    fi
}

# Main menu
case "${1:-menu}" in
    "terminal")
        show_terminal_log
        ;;
    "dashboard") 
        show_dashboard_log
        ;;
    "errors")
        search_errors
        ;;
    "monitor")
        monitor_live
        ;;
    "menu"|*)
        echo "Choose an option:"
        echo "1) Show terminal log"
        echo "2) Show dashboard process log"
        echo "3) Search for errors"
        echo "4) Monitor live"
        echo ""
        read -p "Enter choice (1-4): " choice
        
        case $choice in
            1) show_terminal_log ;;
            2) show_dashboard_log ;;
            3) search_errors ;;
            4) monitor_live ;;
            *) echo "Invalid choice" ;;
        esac
        ;;
esac
