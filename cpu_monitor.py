"""
Pi CPU Monitor
==============
Monitors your Raspberry Pi's system stats and sends them
to your meow meow scratch API. No extra hardware needed!

Tracks: CPU temperature, CPU usage, memory usage, disk usage.

How it works:
  The script runs in a loop: every 60 seconds it reads your Pi's
  CPU temperature, CPU usage, memory, and disk space, then sends
  all of that to your meow meow scratch dashboard so you can check
  on your Pi from anywhere (even your phone!).

Setup:
  pip install -r requirements.txt
  export MEOW_API_KEY="your-key"
  python cpu_monitor.py
"""

# --- Imports ---
# os: lets us read environment variables (like your API key)
import os
# sys: lets us exit the program early if something is wrong
import sys
# time: gives us time.sleep() so we can pause between readings
import time
# psutil: a library that lets Python ask your computer about its
# CPU, memory, and disk -- like a health check-up for your Pi
import psutil
# Meow: the main class from the meow meow scratch SDK that sends data
# MeowError: the error type that Meow raises when something goes wrong
#   (e.g., bad API key, no internet connection)
from meow_sdk import Meow, MeowError

# --- Configuration ---

# Read the API key from an environment variable. Environment variables are
# like secret notes you leave for programs -- they keep your key out of the
# code so you don't accidentally share it.
API_KEY = os.environ.get("MEOW_API_KEY")
if not API_KEY:
    print("Set MEOW_API_KEY environment variable")
    sys.exit(1)

# The name of your app and endpoint on meow meow scratch.
# These must match what you created on your dashboard.
APP = "pi-cpu-monitor"
ENDPOINT = "stats"

# How many seconds to wait between readings. 60 means the script
# sends a new snapshot of your Pi's health once every minute.
INTERVAL = 60  # seconds


def get_cpu_temp():
    """Read CPU temperature from the Pi's thermal zone."""
    try:
        # /sys/class/thermal/thermal_zone0/temp is a special file where
        # Linux writes the CPU temperature. It's not a "real" file on disk --
        # the operating system creates it on the fly so programs can read
        # hardware info as easily as reading a text file.
        with open("/sys/class/thermal/thermal_zone0/temp") as f:
            # The value in this file is in millidegrees Celsius.
            # For example, 48250 means 48.250 degrees. We divide by 1000
            # to convert to normal degrees and round to 1 decimal place.
            return round(int(f.read().strip()) / 1000, 1)
    except (FileNotFoundError, ValueError):
        # FileNotFoundError: this file only exists on a Raspberry Pi (or
        #   similar Linux devices with a thermal sensor). If you're testing
        #   on a regular computer, the file won't be there -- that's fine,
        #   we just return None so the rest of the script keeps working.
        # ValueError: if the file somehow contains unexpected text instead
        #   of a number, we handle that gracefully too.
        return None


def get_stats():
    """Gather all system stats into a dictionary."""
    cpu_temp = get_cpu_temp()

    # cpu_percent(interval=1) measures how busy the CPU is over a 1-second
    # window. It deliberately pauses for 1 second to compare two snapshots
    # of CPU activity -- that's why interval=1 "blocks" (waits) briefly.
    cpu_pct = psutil.cpu_percent(interval=1)

    # virtual_memory() returns a snapshot of your Pi's RAM usage.
    # It includes total memory, used memory, percentage used, etc.
    mem = psutil.virtual_memory()

    # disk_usage("/") checks how full the main storage (SD card) is.
    # The "/" means the root of the filesystem -- the top-level drive.
    disk = psutil.disk_usage("/")

    # Build a dictionary (a set of labeled values) with all the stats.
    # This is the data we'll send to the meow meow scratch API.
    return {
        "cpu_temp_c": cpu_temp,
        "cpu_percent": cpu_pct,
        "memory_percent": mem.percent,
        # mem.used is in bytes. Bytes are tiny -- 1 megabyte = 1,048,576
        # bytes. Dividing by 1024 twice converts bytes -> kilobytes -> megabytes.
        "memory_used_mb": round(mem.used / 1024 / 1024),
        "disk_percent": disk.percent,
        # disk.used is also in bytes. Dividing by 1024 three times converts
        # bytes -> kilobytes -> megabytes -> gigabytes.
        "disk_used_gb": round(disk.used / 1024 / 1024 / 1024, 1),
    }


def main():
    # Create a Meow client using your API key. This object handles all the
    # details of talking to the meow meow scratch API.
    api = Meow(api_key=API_KEY)
    print(f"CPU monitor running — sending every {INTERVAL}s")
    print("Press Ctrl+C to stop\n")

    # --- Main loop: read -> send -> sleep -> repeat ---
    # This runs forever until you press Ctrl+C.
    while True:
        # Step 1: READ -- gather all the current stats from the Pi
        stats = get_stats()
        try:
            # Step 2: SEND -- push the stats to your meow meow scratch dashboard
            api.send(APP, ENDPOINT, stats)

            # Print a summary to the terminal so you can see it's working.
            # If cpu_temp_c is None (not on a Pi), show "N/A" instead.
            temp = f"{stats['cpu_temp_c']}°C" if stats["cpu_temp_c"] else "N/A"
            print(
                f"CPU: {stats['cpu_percent']}% @ {temp} | "
                f"Mem: {stats['memory_percent']}% | "
                f"Disk: {stats['disk_percent']}%"
            )
        except MeowError as e:
            # If sending fails (bad API key, no internet, server down, etc.),
            # we catch the error, print a message, and keep going. The script
            # doesn't crash -- it will try again on the next cycle.
            print(f"Send failed: {e}")

        # Step 3: SLEEP -- wait 60 seconds before the next reading.
        # This keeps us from flooding the API with too many requests.
        time.sleep(INTERVAL)
        # Step 4: REPEAT -- the while loop goes back to step 1 automatically.


if __name__ == "__main__":
    main()
