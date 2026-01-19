import time
import signal
import sys
import multiprocessing as mp
import io
import traceback

import board
from PIL import Image, ImageOps
from pictex import Column, Canvas, Text
from humanize import naturalsize

from adafruit_rgb_display import st7789
from system_stats import SystemStats
from stat_row import StatRow
from display_config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, CS_PIN, DC_PIN, RESET_PIN, 
    BAUDRATE, DISPLAY_CONFIG, TITLE_FONT_SIZE, STATS_FONT_SIZE
)

MAIN_FONT = "./fonts/FiraCodeNerdFont-Light.ttf"

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
    blank_image_final = create_blank_image()
    send_image_to_display(blank_image_final)
    print("blank image sent...")
    sys.exit(0)


signal.signal(signal.SIGTERM, shutdown_handler)

ip_stat = StatRow(
    icon="\uef09",
    label="",
    color="lightblue",
    get_stat=SystemStats.get_ip_address,
    state_string=lambda stat: stat,
    is_warning=lambda stat: False,
    is_critical=lambda stat: False,
)

cpu_stat = StatRow(
    icon="\uf4bc",
    label="",
    color="yellow",
    get_stat=SystemStats.get_cpu_stats,
    state_string=lambda stat: f"{stat:.2f}%",
    is_warning=lambda stat: stat >= 70,
    is_critical=lambda stat: stat >= 90,
)

mem_stat = StatRow(
    icon="\uefc5",
    label="",
    color="lightgreen",
    get_stat=SystemStats.get_memory_stats,
    state_string=lambda memory: f"{naturalsize(memory.used, False, True)}/{naturalsize(memory.total, False, True)} ({(memory.percent):.0f}%)",
    is_warning=lambda memory: memory.percent >= 70,
    is_critical=lambda memory: memory.percent >= 85,
)

disk_stat = StatRow(
    icon="\uf472",
    label="",
    color="lightcyan",
    get_stat=SystemStats.get_disk_stats,
    state_string=lambda disk: f"{naturalsize(disk.used, False, True)}/{naturalsize(disk.total, False, True)} ({(disk.used / disk.total) * 100:.0f}%)",
    is_warning=lambda disk: ((disk.used / disk.total) * 100) >= 80,
    is_critical=lambda disk: ((disk.used / disk.total) * 100) >= 90,
)

temp_stat = StatRow(
    icon="\uf2c9",
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

title = Text("═ SYSTEM MONITOR ═").font_size(TITLE_FONT_SIZE).color("white")
stats = [ip_stat, cpu_stat, mem_stat, disk_stat, temp_stat]

canvas = Canvas().font_family(MAIN_FONT).size(width, height)

print(f"\uf4bcDisplay initialized: {disp.width}x{disp.height}, rotation: {disp.rotation}")
# Initialize display with blank screen
blank_image = create_blank_image(width, height)
send_image_to_display(blank_image)

try:
    while True:
        def update_stats():
            # Send image to display
            try:
                #print("Timestamp 2:", time.time())
                #title = Text(f"{ts}").font_size(TITLE_FONT_SIZE).color("white")
                stats_rows = [title] + [stat.update_compose().max_width(width) for stat in stats]
                composition = Column(*stats_rows).font_size(STATS_FONT_SIZE)

                pil_image = canvas.render(composition).to_pillow()
                #print("Timestamp 3:", time.time())

                # Ensure RGB mode for display compatibility                
                #print(f"Converting PIL image from {pil_image.mode} to RGB mode")
                pil_image = (pil_image.convert('RGB')) if pil_image.mode != 'RGB' else pil_image

                pil_image = ImageOps.contain(pil_image, (width, height))
                #print("Timestamp 4:", time.time())

                # Send directly to SPI display
                send_image_to_display(pil_image)
                #print("Timestamp 5:", time.time())


            except Exception as e:
                print(f"Error rendering or sending image to display: {e}")                
                traceback.print_exc()
        #print("************Timestamp 1:", time.time())
        # Repeated rendering in Canvas leaks memory pretty quickly. I've tried explicit gc.collect() in addition
        # to malloc_trim, but the process memory never went down, hence this process forking
        proc = mp.Process(target=update_stats)
        proc.start()
        proc.join()

        time.sleep(0.5)
except KeyboardInterrupt:
    shutdown_handler(0, 0)
