import os
import socket
import psutil

# Environment configuration
psutil.PROCFS_PATH = os.getenv("PROCFS_PATH", psutil.PROCFS_PATH)
DISK_ROOT = os.getenv("DISK_ROOT", "/")

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
        except psutil.Error:
            return "N/A"

    @staticmethod
    def get_cpu_stats():
        """Get CPU load average"""
        return psutil.cpu_percent(0.1)

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
        except psutil.Error:
            return 0
