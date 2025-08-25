#!/bin/bash

echo "🚀 Launching Jupyter Lab with Oracle libraries..."
echo "📍 Current directory: $(pwd)"
echo "🔧 Activating virtual environment..."

cd "$(dirname "$0")"
source ../venv/bin/activate

echo "✅ Virtual environment activated"
echo "📚 Available kernels:"
jupyter kernelspec list

echo ""
echo "🎯 IMPORTANT: Select 'HungerHub POC' kernel in your notebook!"
echo "💡 Look for it in: Kernel → Change Kernel → HungerHub POC"
echo ""

jupyter lab --ip=0.0.0.0 --port=8889 --no-browser --allow-root

