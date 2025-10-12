import time
import socket
import psutil
import requests
import skia
from pictex import Row, Column, Canvas, Text
import multiprocessing as mp
import os
from humanize import naturalsize

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
        cpu_load = psutil.getloadavg()[0]
        return cpu_load, f"Load: {cpu_load:.2f}"

    @staticmethod
    def get_memory_stats():
        """Get memory usage statistics"""
        memory = psutil.virtual_memory()
        mem_used_gb = naturalsize(memory.used, False, True)
        mem_total_gb = naturalsize(memory.total, False, True)
        mem_percent = memory.percent
        return (
            mem_percent,
            f" RAM: {mem_used_gb}/{mem_total_gb} ({mem_percent}%)",
        )

    @staticmethod
    def get_disk_stats():
        """Get disk usage statistics"""
        disk = psutil.disk_usage(DISK_ROOT)
        disk_used_gb = naturalsize(disk.used, False, True)
        disk_total_gb = naturalsize(disk.total, False, True)
        disk_percent = (disk.used / disk.total) * 100
        return (
            disk_percent,
            f"Disk: {disk_used_gb}/{disk_total_gb} ({disk_percent:.0f}%)",
        )

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
            return cpu_temp, f"Temp: {cpu_temp:.1f}°C"
        except:
            return 0, "Temp: N/A"


# Font configuration - load once at startup
font_family = "./fonts/JetBrainsMono-SemiBold.ttf"
emoji_font_family = "./fonts/NotoColorEmoji.ttf"

title = Text("═ SYSTEM MONITOR ═").font_size(20).color("white")

network_icon = Text("🌐").font_family(emoji_font_family).color("lightblue")
cpu_icon = Text("⚡").font_family(emoji_font_family).color("yellow")
memory_icon = Text("�").font_family(emoji_font_family).color("lightgreen")
disk_icon = Text("💿").font_family(emoji_font_family).color("lightcyan")
temp_icon = Text("🌡️").font_family(emoji_font_family).color("cyan")


def create_display_composition(
    ip_text,
    cpu_text,
    mem_text,
    disk_text,
    temp_text,
    cpu_load,
    mem_percent,
    disk_percent,
    cpu_temp,
):
    """Create the display composition with all system information"""
    return (
        Column(
            title,
            Row(network_icon, Text(ip_text).color("lightblue")),
            Row(
                cpu_icon,
                Text(cpu_text).color(
                    "yellow"
                    if cpu_load < 2.0
                    else "orange" if cpu_load < 4.0 else "red"
                ),
            ),
            Row(
                memory_icon,
                Text(mem_text).color(
                    "lightgreen"
                    if mem_percent < 70
                    else "orange" if mem_percent < 85 else "red"
                ),
            ),
            Row(
                disk_icon,
                Text(disk_text).color(
                    "lightcyan"
                    if disk_percent < 80
                    else "orange" if disk_percent < 90 else "red"
                ),
            ),
            Row(
                temp_icon,
                Text(temp_text).color(
                    "cyan"
                    if "N/A" in temp_text or cpu_temp < 60
                    else "orange" if cpu_temp < 75 else "red"
                ),
            ),
        )
        .padding(15, 15, 15, 15)
        .font_size(18)
    )

canvas = Canvas().font_family(font_family).size(SCREEN_HEIGHT, SCREEN_WIDTH)
      
while True:
    def update_stats():
        # Collect system statistics
        ip_addr = SystemStats.get_ip_address()
        cpu_load, cpu_text = SystemStats.get_cpu_stats()
        mem_percent, mem_text = SystemStats.get_memory_stats()
        disk_percent, disk_text = SystemStats.get_disk_stats()
        cpu_temp, temp_text = SystemStats.get_temperature_stats()

        # Send image to display server
        try:
            composition = create_display_composition(
                ip_addr,
                cpu_text,
                mem_text,
                disk_text,
                temp_text,
                cpu_load,
                mem_percent,
                disk_percent,
                cpu_temp,
            )

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
