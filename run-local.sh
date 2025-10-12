#!/bin/bash

# Local development script for src/stats.py
# This assumes pibox-framebuffer is already running on localhost:2019

set -e

echo "Setting up local development environment for src/stats.py..."

# Check if virtual environment exists, create if not
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Check if pibox-framebuffer is running
echo "Checking if pibox-framebuffer is running on localhost:2019..."
if curl -s -f http://localhost:2019/health > /dev/null 2>&1; then
    echo "✓ pibox-framebuffer is running on localhost:2019"
else
    echo "⚠️  pibox-framebuffer is not responding on localhost:2019"
    echo "   Make sure to start it first with:"
    echo "   sudo docker run -d --privileged --name pibox-framebuffer -p 2019:2019 \\"
    echo "     --device /dev/mem:/dev/mem \\"
    echo "     --device /dev/gpiomem:/dev/gpiomem \\"
    echo "     --device /dev/spidev0.0:/dev/spidev0.0 \\"
    echo "     --device /dev/spidev0.1:/dev/spidev0.1 \\"
    echo "     ghcr.io/cybermaak/pibox-framebuffer:latest"
    echo ""
    echo "Or use the full stack with: ./run.sh"
    exit 1
fi

echo ""
echo "Starting src/stats.py locally..."
python src/stats.py