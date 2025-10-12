import time
import signal
import sys
import os
import multiprocessing as mp
import array

import requests
import skia
from pictex import Column, Canvas, Text
from humanize import naturalsize

from system_stats import SystemStats
from stat_row import StatRow


SCREEN_HEIGHT = 240
SCREEN_WIDTH = 240

MAIN_FONT = "./fonts/JetBrainsMono-SemiBold.ttf"

HTTP_ENDPOINT = "http://localhost:2019/image"

http_session = requests.Session()


# using https://github.com/kubesail/pibox-framebuffer to render images as it python st7789 libraries cause flickering
def send_png_buffer_to_display(png_buffer):
    """Send PNG buffer to display server via HTTP or Unix socket"""

    # Try HTTP endpoint first (default)
    try:
        response = http_session.post(
            HTTP_ENDPOINT,
            data=png_buffer,
            headers={"Content-Type": "application/octet-stream"},
            timeout=5,
        )
        if response.status_code == 200:
            return response
    except Exception as e:
        print(f"Error sending PNG buffer to display: {e}")
        return None



# RGBA black pixels
pixel_data = array.array("B", [0, 0, 0, 255] * (SCREEN_WIDTH * SCREEN_HEIGHT))
image_info = skia.ImageInfo.Make(
    SCREEN_WIDTH, SCREEN_HEIGHT, skia.kRGBA_8888_ColorType, skia.kOpaque_AlphaType
)
blank_image = skia.Image.MakeRasterData(image_info, pixel_data, SCREEN_WIDTH * 4)
blank_image_buffer = bytes(skia.Image.encodeToData(blank_image, skia.kPNG, 100))

def shutdown_handler(signum, frame):
    print("shutdown_handler...")
    send_png_buffer_to_display(blank_image_buffer)
    print("blank image sent...")
    sys.exit(0)


# atexit.register(exit_handler)
signal.signal(signal.SIGTERM, shutdown_handler)

ip_stat = StatRow(
    icon="🌐",
    label="",
    color="lightblue",
    get_stat=SystemStats.get_ip_address,
    state_string=lambda stat: stat,
    is_warning=lambda stat: False,
    is_critical=lambda stat: False,
)

cpu_stat = StatRow(
    icon="⚡",
    label="CPU: ",
    color="yellow",
    get_stat=SystemStats.get_cpu_stats,
    state_string=lambda stat: f"{stat:.2f}%",
    is_warning=lambda stat: stat >= 70,
    is_critical=lambda stat: stat >= 90,
)

mem_stat = StatRow(
    icon="💾",
    label="RAM: ",
    color="lightgreen",
    get_stat=SystemStats.get_memory_stats,
    state_string=lambda memory: f" {naturalsize(memory.used, False, True)}/{naturalsize(memory.total, False, True)} ({(memory.percent):.0f}%)",
    is_warning=lambda memory: memory.percent >= 70,
    is_critical=lambda memory: memory.percent >= 85,
)

disk_stat = StatRow(
    icon="💿",
    label="Disk: ",
    color="lightcyan",
    get_stat=SystemStats.get_disk_stats,
    state_string=lambda disk: f"{naturalsize(disk.used, False, True)}/{naturalsize(disk.total, False, True)} ({(disk.used / disk.total) * 100:.0f}%)",
    is_warning=lambda disk: ((disk.used / disk.total) * 100) >= 80,
    is_critical=lambda disk: ((disk.used / disk.total) * 100) >= 90,
)

temp_stat = StatRow(
    icon="🌡️",
    label="Temp: ",
    color="cyan",
    get_stat=SystemStats.get_temperature_stats,
    state_string=lambda cpu_temp: f"{cpu_temp:.1f}°C",
    is_warning=lambda cpu_temp: cpu_temp >= 60,
    is_critical=lambda cpu_temp: cpu_temp >= 70,
)

title = Text("═ SYSTEM MONITOR ═").font_size(20).color("white")
stats = [ip_stat, cpu_stat, mem_stat, disk_stat, temp_stat]

canvas = Canvas().font_family(MAIN_FONT).size(SCREEN_HEIGHT, SCREEN_WIDTH)
try:

    while True:

        def update_stats():

            # Send image to display server
            try:
                stats_rows = [title] + [stat.update_compose() for stat in stats]
                composition = Column(*stats_rows).padding(15, 15, 15, 15).font_size(18)

                # Render and get PNG buffer directly from skia_image
                rendered = canvas.render(composition)

                png_data = skia.Image.encodeToData(rendered.skia_image, skia.kPNG, 100)
                png_buffer = bytes(png_data)
                send_png_buffer_to_display(png_buffer)

            except Exception as e:
                print(f"Error rendering or sending image to display: {e}")

        # Repeated rendering in Canvas leaks memory pretty quiickly. I've tried expclicit go.collect() in addition to malloc_trim
        # but the process memmory never went down, hence this process forking
        proc = mp.Process(target=update_stats)
        proc.start()
        proc.join()

        time.sleep(1)
except KeyboardInterrupt:
    shutdown_handler(0,0)
