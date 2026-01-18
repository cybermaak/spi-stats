# Deployment Guide

This guide covers the two deployment options for the SPI Stats Monitor.

## Deployment Options Overview

| Mode | Use Case | Pros | Cons |
|------|----------|------|------|
| **Docker SPI** | Production setups | Containerized + auto-restart | Requires privileged container |
| **Native SPI** | Development, simple setups | Best performance, simple | Manual process management |

## 1. Docker SPI Mode (Recommended for production)

### Quick Setup
```bash
git clone <repository-url>
cd spi-stats
./run.sh
```

### Manual Setup
```bash
# Build the container
sudo docker compose build spi-stats

# Start the service
sudo docker compose up -d

# Check status
sudo docker compose ps
sudo docker compose logs -f spi-stats
```

### Running as a Service
The Docker setup automatically provides service management:

```bash
# Start service
./run.sh

# Stop service
./stop.sh

# Restart service
sudo docker compose restart spi-stats

# View logs
sudo docker compose logs -f spi-stats

# Update and restart
git pull
sudo docker compose up -d --build
```

## 2. Native SPI Mode (Best performance)

### Quick Setup
```bash
git clone <repository-url>
cd spi-stats
./run-local.sh
```

### Manual Setup
```bash
# Install system dependencies
sudo apt update
sudo apt install python3-dev python3-pip python3-venv build-essential

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Test display
python src/test_display.py

# Run stats monitor
python src/stats.py
```

### Running as a Service
```bash
# Create systemd service
sudo nano /etc/systemd/system/spi-stats.service
```

```ini
[Unit]
Description=SPI Stats Monitor
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/spi-stats
ExecStart=/home/pi/spi-stats/.venv/bin/python /home/pi/spi-stats/src/stats.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable spi-stats.service
sudo systemctl start spi-stats.service
sudo systemctl status spi-stats.service
```

## Migration Between Modes

### From Native to Docker
```bash
# Stop native version (Ctrl+C or systemctl stop)
sudo systemctl stop spi-stats.service 2>/dev/null || true

# Start Docker version
./run.sh
```

### From Docker to Native
```bash
# Stop Docker services
./stop.sh

# Run native version
./run-local.sh
```

## Troubleshooting

### Display Issues
```bash
# Test display configuration
python src/test_display.py

# Check SPI is enabled
lsmod | grep spi
ls /dev/spi*

# Check connections and configuration
cat src/display_config.py
```

### Docker Issues
```bash
# Check container status
sudo docker compose ps

# View logs
sudo docker compose logs spi-stats

# Restart container
sudo docker compose restart spi-stats
```

### Performance Issues
```bash
# Monitor resources
htop

# For Docker
sudo docker stats spi-stats

# Check memory usage (pictex can leak)
free -h
```