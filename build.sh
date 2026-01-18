#!/bin/bash

# Build script for SPI stats Docker container

set -e

echo "Building SPI stats Docker image..."
echo "=================================="
echo ""

sudo docker compose build spi-stats

echo ""
echo "Build completed successfully!"
echo ""
echo "Available deployment options:"
echo "1. Docker SPI mode: ./run.sh"
echo "2. Native SPI mode: ./run-local.sh"