#!/bin/bash

# Build script for stats.py Docker container

set -e

echo "Building stats Docker image..."
sudo docker compose build 

echo "Build completed successfully!"
echo "To run the complete stack, use: ./run.sh"
echo "To run just the stats container (assuming pibox-framebuffer is running): sudo docker run --rm --network host stats:latest"