#!/bin/bash

# Run script for the SPI stats monitoring with Docker (Direct SPI mode)
# This uses Docker container with direct SPI hardware access

set -e

echo "Starting SPI Stats Monitor with Docker (Direct SPI mode)..."
echo "========================================================="
echo ""
echo "This will:"
echo "1. Build the spi-stats container with direct SPI support"
echo "2. Start the stats monitoring service with hardware access"
echo ""
echo "Note: This requires privileged container access for SPI hardware"
echo ""

# Build and start the service using docker-compose
echo "Building and starting SPI stats service..."
sudo docker compose up -d --build

echo ""
echo "Service started successfully!"
echo "============================="
echo "- spi-stats is running with direct SPI hardware access"
echo "- Stats are displayed directly on the connected ST7789 display"
echo ""
echo "To view logs:"
echo "  sudo docker compose logs -f spi-stats"
echo ""
echo "To stop service:"
echo "  ./stop.sh"
echo ""
echo "Alternative deployment mode:"
echo "- Native SPI: ./run-local.sh"