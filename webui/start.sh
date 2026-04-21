#!/bin/bash

# Kronos Web UI startup script
echo "======================================================================"
echo "🚀 Starting Kronos Prediction Web UI"
echo "======================================================================"
echo ""

# Get project root directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not installed, please install Python3 first"
    exit 1
fi

echo "✅ Python3 found: $(python3 --version)"

# Check virtual environment
if [ -d ".venv" ]; then
    echo "✅ Activating virtual environment..."
    source .venv/bin/activate
else
    echo "⚠️  Virtual environment not found, using system Python"
fi

# Check dependencies
echo "📦 Checking dependencies..."
if ! python3 -c "import flask, flask_cors, pandas, numpy, plotly" &> /dev/null; then
    echo "⚠️  Missing dependencies, installing..."
    pip3 install -r webui/requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Dependencies installation failed"
        exit 1
    fi
    echo "✅ Dependencies installation completed"
else
    echo "✅ All dependencies installed"
fi

echo ""

# Check model files
echo "🔍 Checking model files..."
if [ -d "model/pretrained_models/Kronos-base" ]; then
    echo "✅ Local model found: Kronos-base (102.3M params)"
    MODEL_SIZE=$(du -sh model/pretrained_models/Kronos-base/model.safetensors | cut -f1)
    echo "   Size: $MODEL_SIZE"
else
    echo "⚠️  Local model not found, will use HuggingFace"
    echo "   Tip: Download local model for faster loading"
fi

echo ""

# Check data files
echo "📊 Checking data files..."
DATA_COUNT=0
if [ -d "data/raw/akshare" ]; then
    DATA_COUNT=$(ls data/raw/akshare/*.csv 2>/dev/null | wc -l | tr -d ' ')
fi
if [ "$DATA_COUNT" -gt 0 ]; then
    echo "✅ Found $DATA_COUNT data files in data/raw/akshare/"
else
    echo "⚠️  No data files found"
    echo "   Tip: Run scripts to fetch stock data"
fi

echo ""

# Check MPS support
echo "⚡ Checking GPU acceleration..."
if python3 -c "import torch; exit(0 if torch.backends.mps.is_available() else 1)" 2>/dev/null; then
    echo "✅ Apple Silicon MPS (GPU) available"
else
    echo "⚠️  MPS not available, will use CPU"
fi

echo ""
echo "======================================================================"
echo "🌐 Starting Web Server..."
echo "======================================================================"
echo ""
echo "📍 Access URL: http://localhost:8080"
echo "🔧 Debug Mode: ON"
echo "💻 Device: Auto-detect (MPS preferred)"
echo "🎯 Default Model: Kronos-base (Local)"
echo ""
echo "Press Ctrl+C to stop server"
echo "======================================================================"
echo ""

# Start application
cd "$SCRIPT_DIR"
python3 app.py
