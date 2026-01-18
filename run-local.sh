#!/bin/bash

# Local development script for direct SPI mode
# This runs the SPI version directly on the host

set -e

echo "Starting SPI Stats Monitor..."
echo "================================"

# Check if we're on a Raspberry Pi
if ! command -v raspi-config &> /dev/null; then
    echo "Warning: This doesn't appear to be a Raspberry Pi"
    echo "The display may not work properly"
fi

# Check if SPI is enabled
if ! lsmod | grep -q spi; then
    echo "Warning: SPI doesn't appear to be enabled"
    echo "Enable SPI with: sudo raspi-config"
    echo "Navigate to Interface Options > SPI > Enable"
fi

# Install system dependencies if needed
echo "Checking system dependencies..."
if ! dpkg -l | grep -q python3-dev; then
    echo "Installing system dependencies..."
    sudo apt update
    sudo apt install -y python3-dev python3-pip python3-venv
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install/upgrade requirements
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Test SPI display
echo "Testing SPI display configuration..."
if python src/test_display.py --test-only 2>/dev/null; then
    echo "✓ SPI display test passed"
else
    echo "⚠️  SPI display test failed"
    echo "   Make sure:"
    echo "   1. SPI is enabled: sudo raspi-config"
    echo "   2. Display is connected properly"
    echo "   3. Check src/display_config.py for correct settings"
    echo ""
    echo "Continuing anyway..."
fi

echo ""
echo "Starting SPI stats monitor..."
echo "Press Ctrl+C to stop"
echo "================================"

python src/stats.py