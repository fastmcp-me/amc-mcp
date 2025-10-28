#!/bin/bash

# AMC MCP Server Startup Script
echo "🎬 Starting AMC MCP Server..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "⬇️ Installing dependencies..."
pip install -r requirements.txt

# Install package in development mode
echo "📦 Installing AMC MCP Server..."
pip install -e .

# Run tests
echo "🧪 Running tests..."
python test_server.py

# Start server
echo "🚀 Starting MCP Server..."
echo "Press Ctrl+C to stop the server"
python -m amc_mcp.server