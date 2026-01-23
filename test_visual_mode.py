#!/usr/bin/env python3
"""
Test script to generate text, visual, and grid mode screenshots
for comparison without requiring actual hardware.
Uses shared rendering module from src/rendering.py.
"""
from rendering import (
    load_fonts,
    render_stats_direct,
    render_stats_visual,
    render_stats_grid
)
from humanize import naturalsize
import sys
from collections import namedtuple

# Add src to path for imports
sys.path.insert(0, './src')


# Constants
TITLE_FONT_SIZE = 20
STATS_FONT_SIZE = 18

# Mock system stats
MemoryStats = namedtuple('MemoryStats', ['used', 'total', 'percent'])
DiskStats = namedtuple('DiskStats', ['used', 'total'])

# Load fonts
title_font, stats_font, icon_font = load_fonts(TITLE_FONT_SIZE, STATS_FONT_SIZE)

# Mock test data
memory = MemoryStats(used=2.4e9, total=7.6e9, percent=32)
disk = DiskStats(used=5.5e9, total=6.6e9)

text_mode_data = [
    {'icon': '\uf109', 'icon_color': 'lightblue', 'value': '192.168.88.46', 'value_color': 'lightblue'},
    {'icon': '\uf4bc', 'icon_color': 'yellow', 'value': '75.60%', 'value_color': 'orange'},
    {'icon': '\uefc5', 'icon_color': 'lightgreen',
        'value': f"{naturalsize(memory.used, False, True)}/{naturalsize(memory.total, False, True)} ({memory.percent:.0f}%)", 'value_color': 'lightgreen'},
    {'icon': '\uf472', 'icon_color': 'lightcyan',
        'value': f"{naturalsize(disk.used, False, True)}/{naturalsize(disk.total, False, True)} ({(disk.used / disk.total) * 100:.0f}%)", 'value_color': 'orange'},
    {'icon': '\uf2c9', 'icon_color': 'cyan', 'value': '66.7°C', 'value_color': 'cyan'},
]

visual_mode_data = [
    {'icon': '\uf109', 'icon_color': 'lightblue', 'label': '192.168.88.46',
        'percentage': 0, 'bar_color': 'lightblue', 'has_bar': False},
    {'icon': '\uf4bc', 'icon_color': 'yellow', 'label': '75.6%', 'percentage': 75.6, 'bar_color': 'orange', 'has_bar': True},
    {'icon': '\uefc5', 'icon_color': 'lightgreen',
        'label': f"{naturalsize(memory.total, False, True)} ({memory.percent:.0f}%)", 'percentage': memory.percent, 'bar_color': 'lightgreen', 'has_bar': True},
    {'icon': '\uf472', 'icon_color': 'lightcyan', 'label': f"{naturalsize(disk.total, False, True)} ({(disk.used / disk.total) * 100:.0f}%)", 'percentage': (
        disk.used / disk.total) * 100, 'bar_color': 'orange', 'has_bar': True},
    {'icon': '\uf2c9', 'icon_color': 'cyan', 'label': '66.7°C', 'percentage': 66.7, 'bar_color': 'cyan', 'has_bar': True},
]

# Generate screenshots
width, height = 240, 240
title = "═ SYSTEM MONITOR ═"

print("Generating text mode screenshot...")
text_image = render_stats_direct(width, height, title, text_mode_data,
                                 title_font, stats_font, icon_font,
                                 STATS_FONT_SIZE, TITLE_FONT_SIZE)
text_image.save("screenshot_text_mode.png")
print("Saved: screenshot_text_mode.png")

print("Generating visual mode (rows) screenshot...")
visual_image = render_stats_visual(width, height, title, visual_mode_data,
                                   title_font, stats_font, icon_font,
                                   STATS_FONT_SIZE, TITLE_FONT_SIZE)
visual_image.save("screenshot_visual_mode.png")
print("Saved: screenshot_visual_mode.png")

print("Generating visual mode (grid) screenshot...")
grid_image = render_stats_grid(width, height, title, visual_mode_data,
                               title_font, stats_font, icon_font,
                               STATS_FONT_SIZE, TITLE_FONT_SIZE)
grid_image.save("screenshot_grid_mode.png")
print("Saved: screenshot_grid_mode.png")

print("\nTest complete! Check the generated images:")
print("  - screenshot_text_mode.png (text mode)")
print("  - screenshot_visual_mode.png (visual mode - rows layout)")
print("  - screenshot_grid_mode.png (visual mode - grid layout)")
