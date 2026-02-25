"""
Pi CPU Monitor
==============
Monitors your Raspberry Pi's system stats and sends them
to your meow meow scratch API. No extra hardware needed!

Tracks: CPU temperature, CPU usage, memory usage, disk usage.

Setup:
  pip install -r requirements.txt
  export MEOW_API_KEY="your-key"
  python cpu_monitor.py
"""

import os
import sys
import time
import psutil
from meow_sdk import Meow, MeowError

API_KEY = os.environ.get("MEOW_API_KEY")
if not API_KEY:
    print("Set MEOW_API_KEY environment variable")
    sys.exit(1)

APP = "pi-cpu-monitor"
ENDPOINT = "stats"
INTERVAL = 60  # seconds


def get_cpu_temp():
    """Read CPU temperature from the Pi's thermal zone."""
    try:
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            return round(int(f.read().strip()) / 1000, 1)
    except (FileNotFoundError, ValueError):
        return None


def get_stats():
    cpu_temp = get_cpu_temp()
    cpu_pct = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    return {
        "cpu_temp_c": cpu_temp,
        "cpu_percent": cpu_pct,
        "memory_percent": mem.percent,
        "memory_used_mb": round(mem.used / 1024 / 1024),
        "disk_percent": disk.percent,
        "disk_used_gb": round(disk.used / 1024 / 1024 / 1024, 1),
    }


def main():
    api = Meow(api_key=API_KEY)
    print(f"CPU monitor running — sending every {INTERVAL}s")
    print("Press Ctrl+C to stop\n")

    while True:
        stats = get_stats()
        try:
            api.send(APP, ENDPOINT, stats)
            temp = f"{stats['cpu_temp_c']}°C" if stats["cpu_temp_c"] else "N/A"
            print(
                f"CPU: {stats['cpu_percent']}% @ {temp} | "
                f"Mem: {stats['memory_percent']}% | "
                f"Disk: {stats['disk_percent']}%"
            )
        except MeowError as e:
            print(f"Send failed: {e}")

        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
