#!/bin/bash

# HungerHub POC Dashboard Launch Script
echo "🍽️ Starting HungerHub Analytics Dashboard..."

# Check if in virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️ No virtual environment detected. Activating venv..."
    source venv/bin/activate
fi

# Check if data exists
if [ ! -f "data/processed/unified/people.csv" ] || [ ! -f "data/processed/unified/services.csv" ]; then
    echo "❌ Data files not found. Running ETL pipeline first..."
    python src/smart_etl_pipeline.py
    if [ $? -ne 0 ]; then
        echo "❌ ETL pipeline failed. Exiting."
        exit 1
    fi
fi

# Run dashboard tests
echo "🧪 Running dashboard tests..."
python src/test_dashboard.py
if [ $? -ne 0 ]; then
    echo "❌ Dashboard tests failed. Please check logs."
    exit 1
fi

echo "✅ Tests passed. Launching dashboard..."
echo ""
echo "🌐 Dashboard will be available at: http://localhost:8501"
echo "📊 Use Ctrl+C to stop the dashboard"
echo ""

# Launch Streamlit dashboard
streamlit run src/dashboard/main_app.py --server.port 8501 --server.address localhost
