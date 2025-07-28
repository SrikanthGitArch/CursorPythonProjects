#!/bin/bash

echo "🚀 WhatsApp Clone Installation Script"
echo "======================================"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Install dependencies
echo "📦 Installing dependencies..."

if pip install --break-system-packages Flask Flask-SocketIO; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    echo "You may need to run with sudo or use a virtual environment"
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p templates

echo "🎉 Installation complete!"
echo ""
echo "To start the WhatsApp Clone:"
echo "  python3 app.py"
echo "  or"
echo "  python3 run.py"
echo ""
echo "Then open http://localhost:5000 in your browser"