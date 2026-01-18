"""
Display configuration for different ST7789 variants.
Modify these settings based on your specific display model.
"""

import board
import digitalio

# Screen dimensions
SCREEN_WIDTH = 240
SCREEN_HEIGHT = 240

# SPI Configuration
CS_PIN = digitalio.DigitalInOut(board.CE0)
DC_PIN = digitalio.DigitalInOut(board.D25)
RESET_PIN = digitalio.DigitalInOut(board.D24)
BAUDRATE = 24000000

# Display Configuration
# Common ST7789 configurations:

# 240x240 Square Display (default)
DISPLAY_CONFIG = {
    "rotation": 180,
    "width": SCREEN_WIDTH,
    "height": SCREEN_HEIGHT,
    "x_offset": 0,
    "y_offset": 70,
}

# Uncomment and modify for other display variants:

# 1.3" 240x240 ST7789
# DISPLAY_CONFIG = {
#     "rotation": 180,
#     "width": 240,
#     "height": 240,
#     "x_offset": 0,
#     "y_offset": 80,
# }

# 1.14" 135x240 ST7789
# DISPLAY_CONFIG = {
#     "rotation": 90,
#     "width": 135,
#     "height": 240,
#     "x_offset": 53,
#     "y_offset": 40,
# }

# 1.47" 172x320 ST7789
# DISPLAY_CONFIG = {
#     "rotation": 90,
#     "width": 172,
#     "height": 320,
#     "x_offset": 34,
#     "y_offset": 0,
# }

# 1.9" 170x320 ST7789
# DISPLAY_CONFIG = {
#     "rotation": 270,
#     "width": 170,
#     "height": 320,
#     "x_offset": 35,
#     "y_offset": 0,
# }