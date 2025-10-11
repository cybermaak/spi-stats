#!/bin/bash

# Run script for the complete stats monitoring stack

set -e

echo "Starting the complete stats monitoring stack..."
echo "This will:"
echo "1. Pull and start pibox-framebuffer from ghcr.io/cybermaak/pibox-framebuffer:latest"
echo "2. Build and start the stats monitoring service"
echo ""

# Pull the latest pibox-framebuffer image
echo "Pulling latest pibox-framebuffer image..."
sudo docker pull ghcr.io/cybermaak/pibox-framebuffer:latest

# Start the stack using docker-compose
echo "Starting services with docker-compose..."
sudo docker compose up -d

echo ""
echo "Services started successfully!"
echo "- pibox-framebuffer is running on localhost:2019"
echo "- stats service is monitoring system and sending data to the display"
echo ""
echo "To view logs:"
echo "  sudo docker compose logs -f pibox-framebuffer"
echo "  sudo docker compose logs -f stats"
echo ""
echo "To stop services:"
echo "  sudo docker compose down"