# Repository Structure

This document explains the complete structure and organization of the SPI Stats Monitor repository.

## File Organization

```
spi-stats/
├── src/                          # Source code
│   ├── stats.py                  # Main SPI display application
│   ├── test_display.py           # Display hardware test
│   ├── display_config.py         # Display configuration
│   ├── system_stats.py           # System statistics collection
│   └── stat_row.py               # UI component for stat rows
├── fonts/                        # Font files
│   ├── JetBrainsMono-SemiBold.ttf
│   └── NotoColorEmoji.ttf
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Docker container definition
├── docker-compose.yml           # Docker stack configuration
├── run.sh                        # Start Docker stack
├── run-local.sh                  # Start native SPI mode
├── build.sh                      # Build Docker image
├── stop.sh                       # Stop Docker stack
├── install-deps.sh               # Install SPI dependencies
├── README.md                     # Main documentation
├── INSTALL.md                    # Installation guide
├── DEPLOYMENT.md                 # Deployment guide
└── REPOSITORY.md                 # This file
```

## Source Code Files

### Core Application Files

**`src/stats.py`** - Main application
- Uses `adafruit_rgb_display` for direct SPI communication
- Converts Skia images to PIL for display
- Works in both Docker and native environments
- Includes debug output for image dimensions

### Support Files

**`src/test_display.py`** - Hardware test utility
- Tests SPI display functionality
- Supports quick test mode (`--test-only`)
- Validates display configuration
- Shows colored screens and test patterns

**`src/display_config.py`** - Display configuration
- Centralized display settings
- Support for multiple ST7789 variants
- Pin assignments and display parameters
- Easy to modify for different hardware

**`src/system_stats.py`** - System statistics collection
- CPU, memory, disk, temperature monitoring
- Cross-platform compatibility
- Configurable via environment variables
- Handles Docker volume mounts for host stats

**`src/stat_row.py`** - UI component
- Renders individual statistic rows
- Color-coded warnings and critical states
- Icon and text formatting
- Reusable component architecture

## Configuration Files

### Python Dependencies

**`requirements.txt`** - All dependencies
```
psutil>=5.9.0
pictex>=1.5.0
skia-python>=138.0
humanize>=4.13.0
adafruit-circuitpython-rgb-display
pillow
adafruit-blinka
RPi.GPIO
spidev
```

### Docker Configuration

**`Dockerfile`** - Container definition
- Based on Python 3.13 slim
- Installs graphics and SPI libraries
- Uses `requirements.txt`
- Runs `stats.py` with direct SPI access
- Includes health checks

**`docker-compose.yml`** - Stack orchestration
- Single spi-stats service
- Privileged mode for hardware access
- Volume mounts for host system access
- Health checks and restart policies
- Device mounts for SPI hardware

## Script Files

### Deployment Scripts

**`run.sh`** - Docker deployment
- Builds and starts SPI container
- Direct SPI hardware access
- Production-ready deployment

**`run-local.sh`** - Native SPI deployment
- Creates Python virtual environment
- Installs SPI dependencies
- Tests display configuration
- Starts native SPI version

### Utility Scripts

**`build.sh`** - Docker image builder
- Builds spi-stats container
- Provides deployment guidance
- Used by CI/CD pipelines

**`stop.sh`** - Service stopper
- Stops Docker stack cleanly
- Preserves data and configuration

**`install-deps.sh`** - Dependency installer
- Installs system packages
- Creates Python environment
- Installs SPI libraries
- Validates SPI configuration

**`test-deployment.sh`** - Deployment validator
- Tests all deployment modes
- Validates configuration files
- Checks Python syntax
- Verifies Docker configuration
- Tests fallback mode functionality

## Documentation Files

**`README.md`** - Main documentation
- Project overview
- Quick start guides
- Feature comparison
- Basic troubleshooting

**`INSTALL.md`** - Installation guide
- Hardware setup instructions
- Software installation steps
- Configuration options
- Detailed troubleshooting

**`DEPLOYMENT.md`** - Deployment guide
- Production deployment strategies
- Service configuration
- Monitoring and maintenance
- Security considerations

**`REPOSITORY.md`** - This file
- Repository structure explanation
- File purpose and relationships
- Development workflow guidance

## Development Workflow

### For New Features
1. Test with `src/test_display.py` on hardware
2. Update `src/stats.py` for both Docker and native modes
3. Test Docker deployment with `./run.sh`
4. Test native deployment with `./run-local.sh`

### For Configuration Changes
1. Modify `src/display_config.py` for display settings
2. Update `requirements.txt` for dependencies
3. Adjust `docker-compose.yml` for Docker settings
4. Test both deployment modes

### For Bug Fixes
1. Reproduce issue in appropriate mode
2. Apply fixes to `src/stats.py`
3. Test both Docker and native modes

## Deployment Decision Matrix

| Requirement | Docker SPI | Native SPI |
|-------------|------------|------------|
| New setup | ✅ Recommended | ✅ Good |
| Production | ✅ Excellent | ⚠️ Manual mgmt |
| Development | ✅ Good | ✅ Excellent |
| Performance | ✅ Excellent | ✅ Best |
| Maintenance | ✅ Automated | ⚠️ Manual |
| Monitoring | ✅ Built-in | ⚠️ Manual |

## Version Compatibility

### Hardware Support
- Raspberry Pi (all models with GPIO)
- ST7789 displays (240x240, 135x240, etc.)
- SPI interface required

### Software Requirements
- Python 3.7+ (tested with 3.13)
- Docker 20.10+ (for Docker mode)
- Docker Compose v2+ (for Docker mode)

### Operating System
- Raspberry Pi OS (recommended)
- Ubuntu 20.04+ on ARM64
- Other Linux distributions (may require adjustments)

This repository structure supports multiple deployment scenarios while maintaining code reusability and clear separation of concerns.