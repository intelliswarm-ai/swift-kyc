#!/bin/bash

echo "========================================"
echo "KYC Analysis System - Web UI"
echo "========================================"
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/update requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Check if Ollama is accessible
echo
echo "Checking Ollama connection..."
if curl -s http://172.21.16.1:11434/api/version >/dev/null 2>&1; then
    echo "✅ Ollama is connected"
else
    echo "⚠️  WARNING: Cannot connect to Ollama at http://172.21.16.1:11434"
    echo "Make sure Ollama is running with: ollama serve"
    echo
fi

# Set environment variables
export OLLAMA_BASE_URL=http://172.21.16.1:11434
export OLLAMA_MODEL=mistral

# Run Streamlit
echo
echo "Starting KYC Web UI..."
echo "Access the application at: http://localhost:8501"
echo
echo "Press Ctrl+C to stop the server"
echo "========================================"
streamlit run streamlit_app.py