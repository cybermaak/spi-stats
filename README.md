# Stats Monitor for Raspberry Pi Display

This project provides system monitoring stats displayed on a Raspberry Pi with an SPI display using direct SPI communication with ST7789 displays via the Adafruit CircuitPython RGB Display library.

## Display Mode

The project uses **Direct SPI Display** communication which provides:
- Direct hardware communication via SPI
- Support for multiple ST7789 display variants (240x240, 135x240, etc.)
- Configurable display settings
- Better performance and reliability
- No external dependencies

## Quick Start

### Option 1: Docker with Direct SPI (Recommended)

Containerized deployment with direct hardware access:

```bash
./run.sh
```

This provides the benefits of Docker (isolation, auto-restart, easy management) while using direct SPI communication for optimal performance.

### Option 2: Native Direct SPI

Direct hardware communication without Docker:

```bash
./run-local.sh
```

This script will automatically:
- Install system dependencies
- Create a Python virtual environment
- Install required packages
- Test the display
- Start the stats monitor

## Display Configuration

The direct SPI mode supports various ST7789 display configurations. Edit `src/display_config.py` to match your display:

```python
# 240x240 Square Display (default)
DISPLAY_CONFIG = {
    "rotation": 0,
    "width": 240,
    "height": 240,
    "x_offset": 0,
    "y_offset": 0,
}

# 1.14" 135x240 ST7789
# DISPLAY_CONFIG = {
#     "rotation": 90,
#     "width": 135,
#     "height": 240,
#     "x_offset": 53,
#     "y_offset": 40,
# }
```

Common display variants are included as commented examples in the config file.

## Hardware Requirements

### For Direct SPI Mode:
- Raspberry Pi with SPI enabled
- ST7789 display connected via SPI
- Standard connections:
  - CS: CE0 (GPIO 8)
  - DC: GPIO 25
  - RST: GPIO 24
  - SPI MOSI, SCLK as usual

### SPI Setup:
Enable SPI on your Raspberry Pi:
```bash
sudo raspi-config
# Navigate to Interface Options > SPI > Enable
```

## Project Structure

```
src/
├── stats.py              # Main stats monitor (direct SPI)
├── stats_fallback.py     # Fallback version (saves to files)
├── test_display.py       # Display test utility
├── display_config.py     # Display configuration
├── system_stats.py       # System statistics collection
└── stat_row.py           # UI component for stat rows
```

## Dependencies

### Direct SPI Mode:
- `adafruit-circuitpython-rgb-display` - Display driver
- `adafruit-blinka` - CircuitPython compatibility
- `pillow` - Image processing
- `pictex` - UI rendering
- `skia-python` - Graphics rendering
- `psutil` - System statistics
- `humanize` - Human-readable formatting

### HTTP Server Mode:
- All of the above plus `requests` for HTTP communication

## Development

### Testing Display Configuration

Run the test script to verify your display works:

```bash
python src/test_display.py
```

This will show colored screens and test patterns to verify proper display operation.

### Fallback Mode for Development

When developing without hardware, use the fallback mode:

```bash
python src/stats_fallback.py
```

This saves rendered images to `./output/` directory so you can see what would be displayed.

## Docker Support (Direct SPI Mode)

The Docker setup provides direct SPI communication within containers:

### Quick Start with Docker

```bash
# Build and run the SPI container
./run.sh

# Or manually:
sudo docker compose up -d --build
```

### Docker Architecture

- **spi-stats**: Single container with direct SPI hardware access
- **Privileged mode**: Required for GPIO and SPI device access
- **Volume mounts**: Host system stats and hardware devices

### Docker Compose Configuration

```yml
services:
  spi-stats:
    build: .
    privileged: true
    devices:
      - /dev/mem:/dev/mem
      - /dev/gpiomem:/dev/gpiomem
      - /dev/spidev0.0:/dev/spidev0.0
      - /dev/spidev0.1:/dev/spidev0.1
    volumes:
      - /proc:/host/proc:ro
      - /:/host/disk_root:ro
    restart: unless-stopped
    environment:
      - PROCFS_PATH=/host/proc
      - DISK_ROOT=/host/disk_root
```

### Docker Commands

```bash
# Build and start (recommended)
./run.sh

# Build only
./build.sh

# Stop service
./stop.sh

# View logs
sudo docker compose logs -f spi-stats
```

### Native Commands

```bash
# Run native SPI version
./run-local.sh

# Test display only
python src/test_display.py

# Manual run (after setup)
python src/stats.py
```

### Why Use Docker SPI Mode?

- **Production deployment**: Containerized service with health checks
- **Isolation**: Application runs in isolated container
- **Automatic restart**: Service restarts automatically on failure
- **Easy management**: Standard Docker tooling
- **Direct hardware access**: Optimal performance
- **Consistent environment**: Same runtime regardless of host setup

## Troubleshooting

### Display Not Working:
1. Verify SPI is enabled: `lsmod | grep spi`
2. Check connections match your `display_config.py`
3. Run `python src/test_display.py` to test basic functionality
4. Try different rotation values (0, 90, 180, 270)

### Permission Issues:
- Ensure your user is in the `spi` and `gpio` groups
- Run with `sudo` if needed for hardware access

### Import Errors:
- Install all requirements: `pip install -r requirements.txt`
- For Raspberry Pi, you may need: `sudo apt install python3-dev`

**Inspiration:** 

I have a KubeSail PiBox which is still a nice Raspberry Pi enclosure, but its ecosystem became obsolete with the retirement of the KubeSail project ([PiBox docs here](https://docs.kubesail.com/pibox/) and this is a [wayback link](https://web.archive.org/web/20250919190846/https://docs.kubesail.com/pibox/) in case the docs also die). 

After reflashing the Pi, I couldn't find a decent out-of-box solution for displaying stats on the enclosure's ST7789 display, hence this project. This implementation uses direct SPI communication for optimal performance and reliability.

This is how the stats look:

![screenshot](./screenshot.png)

