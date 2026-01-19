import time
import signal
import sys
import multiprocessing as mp
import traceback

import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
from humanize import naturalsize

from adafruit_rgb_display import st7789
from system_stats import SystemStats
from stat_row import StatRow
from display_config import (CS_PIN, DC_PIN, RESET_PIN, BAUDRATE, DISPLAY_CONFIG, TITLE_FONT_SIZE, STATS_FONT_SIZE)

MAIN_FONT = "./fonts/FiraCodeNerdFont-Light.ttf"

# Color mapping for PIL
COLOR_MAP = {
    'white': (255, 255, 255),
    'lightblue': (173, 216, 230),
    'yellow': (255, 255, 0),
    'lightgreen': (144, 238, 144),
    'lightcyan': (224, 255, 255),
    'cyan': (0, 255, 255),
    'red': (255, 0, 0),
    'orange': (255, 165, 0),
    'black': (0, 0, 0)
}

# Load fonts once at startup
try:
    title_font = ImageFont.truetype(MAIN_FONT, TITLE_FONT_SIZE)
    stats_font = ImageFont.truetype(MAIN_FONT, STATS_FONT_SIZE)
    icon_font = ImageFont.truetype(MAIN_FONT, STATS_FONT_SIZE)
except OSError:
    # Fallback to default font if custom font fails
    title_font = ImageFont.load_default()
    stats_font = ImageFont.load_default()
    icon_font = ImageFont.load_default()

# Setup SPI bus using hardware SPI:
spi = board.SPI()

# Create the ST7789 display with configuration
disp = st7789.ST7789(
    spi,
    cs=CS_PIN,
    dc=DC_PIN,
    rst=RESET_PIN,
    baudrate=BAUDRATE,
    **DISPLAY_CONFIG
)

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


def render_stats_direct(width, height, title_text, stats_data):
    # Create black background
    image = Image.new("RGB", (width, height), COLOR_MAP['black'])
    draw = ImageDraw.Draw(image)

    # Layout constants based on the screenshot
    y_offset = 10  # Top margin
    row_height = 32  # Height per row (including spacing)
    icon_x = 10    # Icon X position
    value_x = 40   # Value text X position

    # Draw title centered at top
    title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (width - title_width) // 2
    draw.text((title_x, y_offset), title_text, fill=COLOR_MAP['white'], font=title_font)

    # Start drawing stats rows
    current_y = y_offset + 35  # Space after title

    for stat_data in stats_data:
        # Draw icon (left aligned)
        draw.text((icon_x, current_y), stat_data['icon'],
                  fill=COLOR_MAP[stat_data['icon_color']], font=icon_font)

        # Draw value (right of icon)
        draw.text((value_x, current_y), stat_data['value'],
                  fill=COLOR_MAP[stat_data['value_color']], font=stats_font)

        current_y += row_height

    return image


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
)

cpu_stat = StatRow(
    icon="\uf4bc",  # CPU icon
    label="",
    color="yellow",
    get_stat=SystemStats.get_cpu_stats,
    state_string=lambda stat: f"{stat:.2f}%",
    is_warning=lambda stat: stat >= 70,
    is_critical=lambda stat: stat >= 90,
)

mem_stat = StatRow(
    icon="\uefc5",  # Memory icon
    label="",
    color="lightgreen",
    get_stat=SystemStats.get_memory_stats,
    state_string=lambda memory: f"{naturalsize(memory.used, False, True)}/{naturalsize(memory.total, False, True)} ({(memory.percent):.0f}%)",
    is_warning=lambda memory: memory.percent >= 70,
    is_critical=lambda memory: memory.percent >= 85,
)

disk_stat = StatRow(
    icon="\uf472",  # Disk icon
    label="",
    color="lightcyan",
    get_stat=SystemStats.get_disk_stats,
    state_string=lambda disk: f"{naturalsize(disk.used, False, True)}/{naturalsize(disk.total, False, True)} ({(disk.used / disk.total) * 100:.0f}%)",
    is_warning=lambda disk: ((disk.used / disk.total) * 100) >= 80,
    is_critical=lambda disk: ((disk.used / disk.total) * 100) >= 90,
)

temp_stat = StatRow(
    icon="\uf2c9",  # Temperature icon
    label="",
    color="cyan",
    get_stat=SystemStats.get_temperature_stats,
    state_string=lambda cpu_temp: f"{cpu_temp:.1f}°C",
    is_warning=lambda cpu_temp: cpu_temp >= 60,
    is_critical=lambda cpu_temp: cpu_temp >= 70,
)

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

print(f"Display initialized: {disp.width}x{disp.height}, rotation: {disp.rotation}")
# Initialize display with blank screen
blank_image = create_blank_image(width, height)
send_image_to_display(blank_image)

try:
    while True:
        def update_stats():
            # Send image to display
            try:
                # Collect current stats data
                stats_data = [stat.update_compose() for stat in stats]

                # Render directly with PIL for optimal performance
                pil_image = render_stats_direct(width, height, title_text, stats_data)
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

        time.sleep(0.5)
except KeyboardInterrupt:
    shutdown_handler(0, 0)
