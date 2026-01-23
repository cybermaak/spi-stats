import time
import signal
import sys
import multiprocessing as mp
import traceback

import board
import digitalio
from PIL import Image
from humanize import naturalsize

from adafruit_rgb_display import st7789
from system_stats import SystemStats
from stat_row import StatRow
from display_config import (CS_PIN, DC_PIN, RESET_PIN, BAUDRATE, DISPLAY_CONFIG,
                            TITLE_FONT_SIZE, STATS_FONT_SIZE, DISPLAY_MODE,
                            DISPLAY_LAYOUT)
from rendering import (load_fonts, render_stats_direct, render_stats_visual,
                       render_stats_grid)

# Load fonts once at startup
title_font, stats_font, icon_font = load_fonts(TITLE_FONT_SIZE, STATS_FONT_SIZE)

# Setup SPI bus using hardware SPI:
spi = board.SPI()

# Create the ST7789 display with configuration
disp = st7789.ST7789(spi,
                     cs=CS_PIN,
                     dc=DC_PIN,
                     rst=RESET_PIN,
                     baudrate=BAUDRATE,
                     **DISPLAY_CONFIG)

# in one instance the display backlight just turned off and won't turn on even with reboot
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True


def send_image_to_display(pil_image):
    """Send PIL Image directly to SPI display"""
    try:
        disp.image(pil_image)
        return True
    except Exception as e:
        print(f"Error sending image to display: {e}")
        image_size = pil_image.size
        # Print the width and height from the tuple
        print(f"3.Image size (width, height): {image_size}")
        traceback.print_exc()
        return False


def create_blank_image(width, height):
    """Create a blank black image"""
    return Image.new("RGB", (width, height), (0, 0, 0))


def shutdown_handler(_signum, _frame):
    print("shutdown_handler...")
    # Use display dimensions directly since width/height may not be in scope
    if disp.rotation % 180 == 90:
        h = disp.width
        w = disp.height
    else:
        w = disp.width
        h = disp.height
    blank_image_final = create_blank_image(w, h)
    send_image_to_display(blank_image_final)
    print("blank image sent...")
    sys.exit(0)


signal.signal(signal.SIGTERM, shutdown_handler)

ip_stat = StatRow(
    icon="\uf109",  # Network icon
    label="",
    color="lightblue",
    get_stat=SystemStats.get_ip_address,
    state_string=lambda stat: stat,
    is_warning=lambda stat: False,
    is_critical=lambda stat: False,
    get_percentage=None,  # IP address has no percentage
    visual_label=lambda stat: stat  # Same as text mode
)

cpu_stat = StatRow(
    icon="\uf4bc",  # CPU icon
    label="",
    color="yellow",
    get_stat=SystemStats.get_cpu_stats,
    state_string=lambda stat: f"{stat:.2f}%",
    is_warning=lambda stat: stat >= 70,
    is_critical=lambda stat: stat >= 90,
    get_percentage=lambda stat: stat,  # CPU returns percentage directly
    visual_label=lambda stat: f"{stat:.1f}%")

mem_stat = StatRow(
    icon="\uefc5",  # Memory icon
    label="",
    color="lightgreen",
    get_stat=SystemStats.get_memory_stats,
    state_string=lambda memory:
    f"{naturalsize(memory.used, False, True)}/{naturalsize(memory.total, False, True)} ({memory.percent:.0f}%)",
    is_warning=lambda memory: memory.percent >= 70,
    is_critical=lambda memory: memory.percent >= 85,
    get_percentage=lambda memory: memory.percent,
    visual_label=lambda memory:
    f"{naturalsize(memory.total, False, True)} ({memory.percent:.0f}%)")

disk_stat = StatRow(
    icon="\uf472",  # Disk icon
    label="",
    color="lightcyan",
    get_stat=SystemStats.get_disk_stats,
    state_string=lambda disk:
    f"{naturalsize(disk.used, False, True)}/{naturalsize(disk.total, False, True)} ({(disk.used / disk.total) * 100:.0f}%)",
    is_warning=lambda disk: ((disk.used / disk.total) * 100) >= 80,
    is_critical=lambda disk: ((disk.used / disk.total) * 100) >= 90,
    get_percentage=lambda disk: (disk.used / disk.total) * 100,
    visual_label=lambda disk:
    f"{naturalsize(disk.total, False, True)} ({(disk.used / disk.total) * 100:.0f}%)"
)

temp_stat = StatRow(
    icon="\uf2c9",  # Temperature icon
    label="",
    color="cyan",
    get_stat=SystemStats.get_temperature_stats,
    state_string=lambda cpu_temp: f"{cpu_temp:.1f}°C",
    is_warning=lambda cpu_temp: cpu_temp >= 60,
    is_critical=lambda cpu_temp: cpu_temp >= 70,
    get_percentage=lambda cpu_temp:
    cpu_temp,  # Use temperature as percentage (0-100°C range)
    visual_label=lambda cpu_temp: f"{cpu_temp:.1f}°C")

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
if disp.rotation % 180 == 90:
    height = disp.width  # we swap height/width to rotate it to landscape!
    width = disp.height
else:
    width = disp.width  # we swap height/width to rotate it to landscape!
    height = disp.height

title_text = "═ SYSTEM MONITOR ═"
stats = [ip_stat, cpu_stat, mem_stat, disk_stat, temp_stat]

print(
    f"Display initialized: {disp.width}x{disp.height}, rotation: {disp.rotation}"
)
print(f"Display mode: {DISPLAY_MODE}, Layout: {DISPLAY_LAYOUT}")
# Initialize display with blank screen
blank_image = create_blank_image(width, height)
send_image_to_display(blank_image)

try:
    while True:

        def update_stats():
            # Send image to display
            try:
                # Choose rendering mode based on configuration
                if DISPLAY_MODE == 'visual':
                    # Collect stats data for visual mode (with progress bars)
                    stats_data = [stat.get_visual_data() for stat in stats]

                    # Choose layout: grid or rows
                    if DISPLAY_LAYOUT == 'grid':
                        pil_image = render_stats_grid(width, height, title_text,
                                                      stats_data, title_font,
                                                      stats_font, icon_font,
                                                      STATS_FONT_SIZE,
                                                      TITLE_FONT_SIZE)
                    else:
                        pil_image = render_stats_visual(width, height,
                                                        title_text, stats_data,
                                                        title_font, stats_font,
                                                        icon_font,
                                                        STATS_FONT_SIZE,
                                                        TITLE_FONT_SIZE)
                else:
                    # Collect stats data for text mode (default)
                    stats_data = [stat.update_compose() for stat in stats]
                    # Render with text mode (rows layout only)
                    pil_image = render_stats_direct(width, height, title_text,
                                                    stats_data, title_font,
                                                    stats_font, icon_font,
                                                    STATS_FONT_SIZE,
                                                    TITLE_FONT_SIZE)

                pil_image.save("screenshot.png")
                # Send directly to SPI display
                send_image_to_display(pil_image)

            except Exception as e:
                print(f"Error rendering or sending image to display: {e}")
                traceback.print_exc()

        # print("************Timestamp 1:", time.time())
        # Process forking used as safety measure for memory management
        # Can be removed if direct PIL rendering proves stable
        proc = mp.Process(target=update_stats)
        proc.start()
        proc.join()

        time.sleep(1)
except KeyboardInterrupt:
    shutdown_handler(0, 0)
