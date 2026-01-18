# Installation Guide

This guide covers setting up the SPI Stats Monitor on a Raspberry Pi with an ST7789 display using direct SPI communication.

## Prerequisites

- Raspberry Pi (any model with GPIO pins)
- ST7789 SPI display (240x240, 135x240, or other variants)
- Python 3.7 or newer
- SPI enabled on the Raspberry Pi

## Hardware Setup

### Standard ST7789 Wiring

Connect your ST7789 display to the Raspberry Pi as follows:

| ST7789 Pin | Raspberry Pi Pin | GPIO | Description |
|------------|------------------|------|-------------|
| VCC        | 3.3V             | -    | Power       |
| GND        | GND              | -    | Ground      |
| SCL/SCLK   | Pin 23           | 11   | SPI Clock   |
| SDA/MOSI   | Pin 19           | 10   | SPI Data    |
| RES/RST    | Pin 18           | 24   | Reset       |
| DC         | Pin 22           | 25   | Data/Command|
| CS         | Pin 24           | 8    | Chip Select |

### Enable SPI

1. Run the Raspberry Pi configuration tool:
```bash
sudo raspi-config
```

2. Navigate to: `Interface Options` → `SPI` → `Enable`

3. Reboot your Raspberry Pi:
```bash
sudo reboot
```

4. Verify SPI is enabled:
```bash
lsmod | grep spi
ls /dev/spi*
```

You should see SPI modules loaded and `/dev/spidev0.0` and `/dev/spidev0.1` devices.

## Software Installation

### Method 1: Automated Setup (Recommended)

1. Clone this repository:
```bash
git clone <repository-url>
cd spi-stats
```

2. Run the local setup script:
```bash
./run-local.sh
```

This will automatically install dependencies, test the display, and start the monitor.

### Method 2: Docker Setup (Production)

1. Clone this repository and run:
```bash
./run.sh
```

This will build and start the Docker container with direct SPI access.

### Method 3: Manual Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd spi-stats
```

2. Create and activate a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Test your display:
```bash
python src/test_display.py
```

5. If the test passes, run the stats monitor:
```bash
python src/stats.py
```

## Configuration

### Display Configuration

Edit `src/display_config.py` to match your specific display:

```python
# For 240x240 displays (default)
DISPLAY_CONFIG = {
    "rotation": 0,
    "width": 240,
    "height": 240,
    "x_offset": 0,
    "y_offset": 0,
}

# For 1.14" 135x240 displays
DISPLAY_CONFIG = {
    "rotation": 90,
    "width": 135,
    "height": 240,
    "x_offset": 53,
    "y_offset": 40,
}
```

### Pin Configuration

If your wiring differs from the standard setup, modify the pin assignments in `src/display_config.py`:

```python
CS_PIN = digitalio.DigitalInOut(board.CE0)    # GPIO 8
DC_PIN = digitalio.DigitalInOut(board.D25)    # GPIO 25
RESET_PIN = digitalio.DigitalInOut(board.D24) # GPIO 24
```

## Troubleshooting

### Display Not Working

1. **Check connections**: Verify all wires are connected properly
2. **Test SPI**: Run `ls /dev/spi*` to ensure SPI devices exist
3. **Check permissions**: Add your user to the `spi` and `gpio` groups:
   ```bash
   sudo usermod -a -G spi,gpio $USER
   ```
   Then log out and back in.

4. **Try different rotations**: Edit `display_config.py` and try rotation values: 0, 90, 180, 270

### Import Errors

**ModuleNotFoundError: No module named 'RPi'**

This error occurs when the Raspberry Pi GPIO library isn't installed:

1. Install system dependencies:
   ```bash
   sudo apt update
   sudo apt install python3-dev python3-pip build-essential
   ```

2. Install RPi.GPIO:
   ```bash
   pip install RPi.GPIO
   ```

3. Or run the automated installer:
   ```bash
   ./install-deps.sh
   ```

**Other import errors for `board` or `adafruit_rgb_display`:**

1. Ensure you're on a Raspberry Pi (these libraries don't work on other systems)
2. Install system dependencies:
   ```bash
   sudo apt update
   sudo apt install python3-dev python3-pip
   ```
3. Reinstall requirements:
   ```bash
   pip install --upgrade -r requirements.txt
   ```

### Permission Denied Errors

If you get permission errors accessing GPIO or SPI:

1. Run with sudo (temporary solution):
   ```bash
   sudo python src/stats.py
   ```

2. Or add your user to the required groups (permanent solution):
   ```bash
   sudo usermod -a -G spi,gpio,i2c $USER
   sudo reboot
   ```

### Display Shows Wrong Colors or Orientation

1. Try different rotation values in `display_config.py`
2. Check if your display needs different offset values
3. Some displays may need `invert=True` parameter

### Memory Issues

The stats monitor uses process forking to handle memory leaks in the rendering library. If you experience issues:

1. Monitor memory usage: `htop` or `free -h`
2. Reduce update frequency by increasing `time.sleep(1)` to `time.sleep(2)` or higher
3. Consider using the fallback mode for testing: `python src/stats_fallback.py`

## Running as a Service

### Docker Service (Recommended)

The Docker approach automatically provides service management:

```bash
# Start service
./run.sh

# Stop service  
./stop.sh

# View logs
sudo docker compose logs -f spi-stats

# Restart service
sudo docker compose restart spi-stats
```

### Native Systemd Service

To run the native version automatically on boot:

1. Create a systemd service file:
```bash
sudo nano /etc/systemd/system/spi-stats.service
```

2. Add the following content (adjust paths as needed):
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

3. Enable and start the service:
```bash
sudo systemctl enable spi-stats.service
sudo systemctl start spi-stats.service
```

4. Check service status:
```bash
sudo systemctl status spi-stats.service
```

## Alternative: Legacy HTTP Mode

If you need compatibility with existing pibox-framebuffer setups, you can still use the HTTP approach by manually setting up pibox-framebuffer and using a custom HTTP client. However, the direct SPI approach is recommended for new installations due to better performance and simpler architecture.