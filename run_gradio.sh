#!/bin/bash
# Gradio Web UI Startup Script for Disaster Response RAG System

echo ""
echo "╔════════════════════════════════════════════════════════════════════════════════╗"
echo "║         Disaster Response RAG - Gradio Web UI                                  ║"
echo "║         Starting interactive web interface...                                  ║"
echo "╚════════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 is not installed or not in PATH"
    echo "Please install Python 3.8+ and try again"
    exit 1
fi

# Check if gradio is installed
if ! python3 -c "import gradio" 2>/dev/null; then
    echo ""
    echo "Gradio not found. Installing..."
    pip install gradio
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install gradio"
        exit 1
    fi
fi

echo ""
echo "✓ All dependencies verified"
echo ""
echo "Starting Gradio app..."
echo ""
echo "The web interface will be available at:"
echo "  - Local:     http://127.0.0.1:7860"
echo "  - Network:   http://<your-ip>:7860"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the Gradio app
python3 gradio_app.py

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Failed to start Gradio app"
    echo "Check your GROQ_API_KEY in .env file"
    echo ""
    exit 1
fi
