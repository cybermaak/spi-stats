#!/bin/bash

# Installation script for SPI Stats Monitor dependencies
# Run this script to install all required system and Python dependencies

set -e

echo "SPI Stats Monitor - Dependency Installation"
echo "=========================================="

# Check if running on Raspberry Pi
if ! command -v raspi-config &> /dev/null; then
    echo "Warning: This doesn't appear to be a Raspberry Pi"
    echo "Some dependencies may not work on other systems"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update package list
echo "Updating package list..."
sudo apt update

# Install system dependencies
echo "Installing system dependencies..."
sudo apt install -y \
    python3 \
    python3-dev \
    python3-pip \
    python3-venv \
    python3-setuptools \
    build-essential \
    git

# Check SPI status
echo "Checking SPI configuration..."
if ! lsmod | grep -q spi; then
    echo "SPI is not enabled!"
    echo "Please enable SPI using: sudo raspi-config"
    echo "Navigate to: Interface Options > SPI > Enable"
    echo "Then reboot and run this script again"
    exit 1
else
    echo "SPI is enabled ✓"
fi

# Check for SPI devices
if [ ! -e "/dev/spidev0.0" ]; then
    echo "Warning: SPI device /dev/spidev0.0 not found"
    echo "You may need to reboot after enabling SPI"
else
    echo "SPI devices found ✓"
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
else
    echo "Virtual environment already exists ✓"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "Installation complete!"
echo "====================="
echo ""
echo "Next steps:"
echo "1. Test your display: python src/test_display.py"
echo "2. Run the stats monitor: python src/stats.py"
echo "3. Or use the convenience script: ./run-spi.sh"
echo ""
echo "If you encounter permission issues, add your user to the spi and gpio groups:"
echo "sudo usermod -a -G spi,gpio \$USER"
echo "Then log out and back in."