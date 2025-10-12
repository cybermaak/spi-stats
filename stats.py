import time
import socket
import psutil
import requests
import skia
from pictex import Row, Column, Canvas, Text
import multiprocessing as mp
import os
from humanize import naturalsize
import atexit

SCREEN_HEIGHT = 240
SCREEN_WIDTH = 240

# Display server configuration
HTTP_ENDPOINT = "http://localhost:2019/image"

http_session = requests.Session()

psutil.PROCFS_PATH = os.getenv("PROCFS_PATH", psutil.PROCFS_PATH)
DISK_ROOT = os.getenv("DISK_ROOT", "/")

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


blank_image = (
    Canvas()
    .size(SCREEN_HEIGHT, SCREEN_WIDTH)
    .background_color("black")
    .render(Text(""))
)
blank_image_buffer = bytes(
    skia.Image.encodeToData(blank_image.skia_image, skia.kPNG, 100)
)


def exit_handler():
    send_png_buffer_to_display(blank_image_buffer)


atexit.register(exit_handler)


class SystemStats:
    """Static class for collecting system statistics"""

    @staticmethod
    def get_ip_address():
        """Get the current IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip_addr = s.getsockname()[0]
            s.close()
            return ip_addr
        except:
            return "N/A"

    @staticmethod
    def get_cpu_stats():
        """Get CPU load average"""
        return psutil.getloadavg()[0]

    @staticmethod
    def get_memory_stats():
        """Get memory usage statistics"""
        return psutil.virtual_memory()

    @staticmethod
    def get_disk_stats():
        """Get disk usage statistics"""
        return psutil.disk_usage(DISK_ROOT)

    @staticmethod
    def get_temperature_stats():
        """Get CPU temperature"""
        cpu_temp = 0
        try:
            temps = psutil.sensors_temperatures()
            if "cpu_thermal" in temps:
                cpu_temp = temps["cpu_thermal"][0].current
            elif "coretemp" in temps:
                cpu_temp = temps["coretemp"][0].current
            else:
                # Fallback to reading thermal zone file
                with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                    cpu_temp = int(f.read().strip()) / 1000
            return cpu_temp
        except:
            return 0


# Font configuration - load once at startup
font_family = "./fonts/JetBrainsMono-SemiBold.ttf"
emoji_font_family = "./fonts/NotoColorEmoji.ttf"


class Stat:
    def __init__(
        self, icon, label, color, get_stat, state_string, is_warning, is_critical
    ):
        self.icon = icon
        self.label = label
        self.color = color
        self.get_stat = get_stat
        self.state_string = state_string
        self.is_warning = is_warning
        self.is_critical = is_critical

    def update_render(self):
        stat = self.get_stat()
        stat_text = self.state_string(stat)
        stat_color = (
            "red"
            if self.is_critical(stat)
            else "orange" if self.is_warning(stat) else self.color
        )

        return Row(
            Text(self.icon).font_family(emoji_font_family),
            Text(self.label).color(self.color),
            Text(stat_text).color(stat_color),
        )


ip_stat = Stat(
    icon="🌐",
    label="",
    color="lightblue",
    get_stat=SystemStats.get_ip_address,
    state_string=lambda stat: stat,
    is_warning=lambda stat: False,
    is_critical=lambda stat: False,
)

cpu_stat = Stat(
    icon="⚡",
    label="Load: ",
    color="yellow",
    get_stat=SystemStats.get_cpu_stats,
    state_string=lambda stat: f"{stat:.2f}",
    is_warning=lambda stat: stat >= 2.0,
    is_critical=lambda stat: stat >= 4.0,
)

mem_stat = Stat(
    icon="💾",
    label="RAM: ",
    color="lightgreen",
    get_stat=SystemStats.get_memory_stats,
    state_string=lambda memory: f" {naturalsize(memory.used, False, True)}/{naturalsize(memory.total, False, True)} ({(memory.percent):.0f}%)",
    is_warning=lambda memory: memory.percent >= 70,
    is_critical=lambda memory: memory.percent >= 85,
)

disk_stat = Stat(
    icon="💿",
    label="Disk: ",
    color="lightcyan",
    get_stat=SystemStats.get_disk_stats,
    state_string=lambda disk: f"{naturalsize(disk.used, False, True)}/{naturalsize(disk.total, False, True)} ({(disk.used / disk.total) * 100:.0f}%)",
    is_warning=lambda disk: ((disk.used / disk.total) * 100) >= 80,
    is_critical=lambda disk: ((disk.used / disk.total) * 100) >= 90,
)

temp_stat = Stat(
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

canvas = Canvas().font_family(font_family).size(SCREEN_HEIGHT, SCREEN_WIDTH)

while True:

    def update_stats():

        # Send image to display server
        try:
            stats_rows = [title] + [stat.update_render() for stat in stats]
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
