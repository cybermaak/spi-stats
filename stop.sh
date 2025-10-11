#!/bin/bash

# Stop script for the stats monitoring stack

set -e

echo "Stopping stats monitoring stack..."
sudo docker compose down

echo "Services stopped successfully!"
echo ""
echo "To start again, use: ./run.sh"