"""
Display configuration for different ST7789 variants.
Configuration can be overridden with environment variables.
"""

import os
import board
import digitalio

# Screen dimensions - configurable via environment variables
SCREEN_WIDTH = int(os.getenv('SCREEN_WIDTH', '240'))
SCREEN_HEIGHT = int(os.getenv('SCREEN_HEIGHT', '240'))

# SPI Configuration
CS_PIN = digitalio.DigitalInOut(board.CE0)
DC_PIN = digitalio.DigitalInOut(board.D25)
RESET_PIN = digitalio.DigitalInOut(board.D24)
BAUDRATE = 24000000

# Display Configuration - configurable via environment variables
DISPLAY_CONFIG = {
    "rotation": int(os.getenv('DISPLAY_ROTATION', '180')),
    "width": SCREEN_WIDTH,
    "height": SCREEN_HEIGHT,
    "x_offset": int(os.getenv('DISPLAY_X_OFFSET', '0')),
    "y_offset": int(os.getenv('DISPLAY_Y_OFFSET', '70')),
}

# Font configuration - configurable via environment variables
TITLE_FONT_SIZE = int(os.getenv('TITLE_FONT_SIZE', '20'))
STATS_FONT_SIZE = int(os.getenv('STATS_FONT_SIZE', '18'))

# Common ST7789 configurations (for reference):

# 240x240 Square Display (default)
# SCREEN_WIDTH=240 SCREEN_HEIGHT=240 DISPLAY_ROTATION=180 DISPLAY_X_OFFSET=0 DISPLAY_Y_OFFSET=70

# 1.3" 240x240 ST7789
# SCREEN_WIDTH=240 SCREEN_HEIGHT=240 DISPLAY_ROTATION=180 DISPLAY_X_OFFSET=0 DISPLAY_Y_OFFSET=80

# 1.14" 135x240 ST7789
# SCREEN_WIDTH=135 SCREEN_HEIGHT=240 DISPLAY_ROTATION=90 DISPLAY_X_OFFSET=53 DISPLAY_Y_OFFSET=40

# 1.47" 172x320 ST7789
# SCREEN_WIDTH=172 SCREEN_HEIGHT=320 DISPLAY_ROTATION=90 DISPLAY_X_OFFSET=34 DISPLAY_Y_OFFSET=0

# 1.9" 170x320 ST7789
# SCREEN_WIDTH=170 SCREEN_HEIGHT=320 DISPLAY_ROTATION=270 DISPLAY_X_OFFSET=35 DISPLAY_Y_OFFSET=0
