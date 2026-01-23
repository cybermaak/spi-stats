#!/bin/bash

# Local run script for SPI Stats Monitor
# This handles dependency installation and runs the SPI version directly on the host

set -e

echo "SPI Stats Monitor"
echo "================="

# Check if we're on a Raspberry Pi
if ! command -v raspi-config &> /dev/null; then
    echo "Warning: This doesn't appear to be a Raspberry Pi"
    echo "Some dependencies may not work on other systems"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check SPI status
echo "Checking SPI configuration..."
if ! lsmod | grep -q spi; then
    echo "Warning: SPI doesn't appear to be enabled"
    echo "Enable SPI with: sudo raspi-config"
    echo "Navigate to Interface Options > SPI > Enable"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✓ SPI is enabled"
fi

# Check for SPI devices
if [ ! -e "/dev/spidev0.0" ]; then
    echo "Warning: SPI device /dev/spidev0.0 not found"
    echo "You may need to reboot after enabling SPI"
else
    echo "✓ SPI devices found"
fi

# Install system dependencies if needed
echo ""
echo "Checking system dependencies..."
NEED_SYSTEM_DEPS=0
for pkg in python3-dev python3-venv curl build-essential; do
    if ! dpkg -l | grep -q "^ii  $pkg"; then
        NEED_SYSTEM_DEPS=1
        break
    fi
done

if [ $NEED_SYSTEM_DEPS -eq 1 ]; then
    echo "Installing system dependencies..."
    sudo apt update
    sudo apt install -y \
        python3 \
        python3-dev \
        python3-venv \
        build-essential \
        git \
        curl
else
    echo "✓ System dependencies installed"
fi

# Install uv if not present
if ! command -v uv &> /dev/null; then
    echo ""
    echo "Installing uv package manager..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
else
    echo "✓ uv is installed"
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo ""
    echo "Creating Python virtual environment..."
    uv venv
else
    echo "✓ Virtual environment exists"
fi

# Install/sync dependencies with uv
echo ""
echo "Syncing Python dependencies..."
uv sync

# Test SPI display
echo ""
echo "Testing SPI display configuration..."
if uv run python src/test_display.py --test-only 2>/dev/null; then
    echo "✓ SPI display test passed"
else
    echo "⚠️  SPI display test failed (or --test-only not supported)"
    echo "   Make sure:"
    echo "   1. SPI is enabled: sudo raspi-config"
    echo "   2. Display is connected properly"
    echo "   3. Check src/display_config.py for correct settings"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "================================"
echo "Starting SPI stats monitor..."
echo "Press Ctrl+C to stop"
echo "================================"
echo ""

uv run python src/stats.py
