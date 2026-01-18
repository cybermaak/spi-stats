#!/usr/bin/env python3
"""
Simple test script to verify the ST7789 display is working.
Run this to test your display configuration before running the main stats program.
"""

import time
import sys
import traceback
import board
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import st7789
from display_config import (
    CS_PIN, DC_PIN, RESET_PIN,
    BAUDRATE, DISPLAY_CONFIG
)

def main():
    # Check for quick test mode
    quick_test = "--test-only" in sys.argv

    print("Initializing ST7789 display...")

    try:
        # Setup SPI bus
        spi = board.SPI()

        # Create display
        disp = st7789.ST7789(
            spi,
            cs=CS_PIN,
            dc=DC_PIN,
            rst=RESET_PIN,
            baudrate=BAUDRATE,
            **DISPLAY_CONFIG
        )

        print(f"Display initialized: {disp.width}x{disp.height}")

    except Exception as e:
        print(f"Failed to initialize display: {e}")
        traceback.print_exc()
        if quick_test:
            sys.exit(1)
        return

    # Create image with proper dimensions
    if disp.rotation % 180 == 90:
        height = disp.width
        width = disp.height
    else:
        width = disp.width
        height = disp.height

    print(f"Image dimensions: {width}x{height}")

    if quick_test:
        # Quick test - just show green screen briefly
        print("Quick test mode - showing green screen...")
        image = Image.new("RGB", (width, height), (0, 255, 0))
        disp.image(image)
        time.sleep(0.5)

        # Clear to black
        image = Image.new("RGB", (width, height), (0, 0, 0))
        disp.image(image)
        print("Quick test completed successfully!")
        return

    # Full test mode
    # Test 1: Solid colors
    colors = [
        ("Red", (255, 0, 0)),
        ("Green", (0, 255, 0)),
        ("Blue", (0, 0, 255)),
        ("White", (255, 255, 255)),
        ("Black", (0, 0, 0))
    ]

    for color_name, color in colors:
        print(f"Testing {color_name}...")
        image = Image.new("RGB", (width, height), color)
        disp.image(image)
        time.sleep(1)

    # Test 2: Text and shapes
    print("Testing text and shapes...")
    image = Image.new("RGB", (width, height), (0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Draw some shapes
    draw.rectangle((10, 10, width-10, height-10), outline=(255, 255, 255), width=2)
    draw.ellipse((20, 20, width-20, height-20), outline=(255, 0, 0), width=2)

    # Draw text
    try:
        # Try to use a system font
        font = ImageFont.load_default()
        draw.text((30, height//2 - 20), "ST7789 Display", fill=(255, 255, 255), font=font)
        draw.text((30, height//2), "Test Successful!", fill=(0, 255, 0), font=font)
        draw.text((30, height//2 + 20), f"{width}x{height}", fill=(255, 255, 0), font=font)
    except Exception as e:
        print(f"Font loading failed: {e}")
        traceback.print_exc()
        draw.text((30, height//2), "Display OK", fill=(255, 255, 255))

    disp.image(image)
    print("Test complete! Display should show text and shapes.")
    print("Press Ctrl+C to exit...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nClearing display...")
        blank = Image.new("RGB", (width, height), (0, 0, 0))
        disp.image(blank)
        print("Done!")


if __name__ == "__main__":
    main()
