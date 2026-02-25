# Pi CPU Monitor

Keep an eye on your Raspberry Pi from anywhere! This script reads your Pi's CPU temperature, CPU usage, memory, and disk space, then sends it to the internet so you can check on it from your phone. Perfect for headless Pis (ones without a monitor).

You just run one Python script, and it quietly reports your Pi's health to your [meow meow scratch](https://meowmeowscratch.com) dashboard every 60 seconds. That's it!

---

## What you'll learn

Even if you've never written code before, by setting up this project you'll pick up real skills:

- **Reading system info with Python** -- Your Pi knows its own temperature, how busy its CPU is, how much memory it's using, and how full its storage is. This script asks for all of that and packages it up neatly.
- **How Linux exposes hardware data as files** -- On Linux (the operating system your Pi runs), hardware information like CPU temperature is written into special files. You can read them just like a text file. It's one of the coolest things about Linux!
- **Unit conversions (bytes to megabytes)** -- Computers measure memory and storage in bytes, but nobody wants to read a 10-digit number. We convert bytes into megabytes (MB) and gigabytes (GB) so the numbers make sense to humans.
- **Sending data to an API on a timer** -- An API is a way for programs to talk to each other over the internet. This script sends your Pi's stats to the meow meow scratch API every 60 seconds, so you can view them from anywhere.

---

## What you'll need

- **A Raspberry Pi** (any model -- Pi Zero, Pi 3, Pi 4, Pi 5, etc.)
- **A meow meow scratch account** -- Sign up free at [meowmeowscratch.com](https://meowmeowscratch.com)

That's it! No extra hardware, no sensors, no wires. Everything this script monitors is already built into your Pi.

---

## Step-by-step setup

### 1. Create your meow meow scratch app

Before running the script, you need a place for the data to go:

1. Log in to your [meow meow scratch](https://meowmeowscratch.com) account.
2. Create a new app called **`pi-cpu-monitor`**.
3. Inside that app, create a collection endpoint called **`stats`**.
4. Add these fields to the `stats` endpoint (set them all to type **number**):
   - `cpu_temp_c`
   - `cpu_percent`
   - `memory_percent`
   - `memory_used_mb`
   - `disk_percent`
   - `disk_used_gb`
5. Copy your **API key** -- you'll need it in a moment.

### 2. Get the code onto your Pi

If you downloaded or cloned this project, open a terminal on your Pi and navigate to the `pi-cpu-monitor` folder:

```bash
cd pi-cpu-monitor
```

### 3. Install the dependencies with pip

Your Pi already has Python installed, but this script needs two extra packages. We install them with **pip**, which is Python's package manager (think of it like an app store for Python libraries).

Run this command:

```bash
pip install -r requirements.txt
```

This installs:

- **`psutil`** -- a library that lets Python ask your computer about its CPU, memory, and disk -- like a health check-up for your Pi. Without it, we'd have to read a bunch of low-level system files ourselves.
- **`meow-sdk`** -- the official meow meow scratch library. It handles all the details of connecting to the meow meow scratch API so you can send data with just one line of code.

> **Tip:** If `pip` doesn't work, try `pip3` instead. Some Pis have both Python 2 and Python 3, and `pip3` makes sure you're using the right one.

### 4. Set your API key

The script needs your meow meow scratch API key to send data. We store it in an **environment variable** -- that's a piece of information you set in your terminal that programs can read. It keeps your secret key out of the code so you don't accidentally share it.

Run this command, replacing `your-key` with the API key you copied earlier:

```bash
export MEOW_API_KEY="your-key"
```

> **What does `export` do?** It creates a temporary variable in your terminal session. The script reads this variable when it starts. If you close your terminal and open a new one, you'll need to run this command again.

### 5. Run the monitor

```bash
python cpu_monitor.py
```

You should see output like this:

```
CPU monitor running — sending every 60s
Press Ctrl+C to stop

CPU: 12.3% @ 48.2°C | Mem: 34.5% | Disk: 21.0%
CPU: 8.1% @ 47.8°C | Mem: 33.9% | Disk: 21.0%
```

Every 60 seconds, it reads your Pi's stats and sends them to your meow meow scratch dashboard. Press **Ctrl+C** at any time to stop it.

---

## How the code works

Here's a plain-English walkthrough of what the script does. You don't need to understand all of this to use it, but it's a great way to start learning Python!

### Reading CPU temperature (the thermal_zone0 file)

```python
with open("/sys/class/thermal/thermal_zone0/temp") as f:
    return round(int(f.read().strip()) / 1000, 1)
```

`/sys/class/thermal/thermal_zone0/temp` is a special file where Linux writes the CPU temperature -- we just read it like any text file. The value is in **millidegrees** (so `48250` means 48.250 degrees Celsius), so we divide by 1000 to get a normal temperature reading. We also round to one decimal place to keep it tidy.

If this file doesn't exist (for example, you're testing on a regular computer instead of a Pi), the script catches the error and returns `None` instead of crashing.

### Gathering all the stats

```python
stats = {
    "cpu_temp_c": cpu_temp,
    "cpu_percent": cpu_pct,
    "memory_percent": mem.percent,
    "memory_used_mb": round(mem.used / 1024 / 1024),
    "disk_percent": disk.percent,
    "disk_used_gb": round(disk.used / 1024 / 1024 / 1024, 1),
}
```

This is a **dictionary** -- a way to store labeled data in Python. Each label (like `"cpu_temp_c"`) is paired with a value. We build this dictionary by asking `psutil` about CPU, memory, and disk usage. The memory and disk numbers come back in bytes, so we convert them:

- **Bytes to megabytes (MB):** divide by 1024 twice (1024 bytes = 1 kilobyte, 1024 kilobytes = 1 megabyte)
- **Bytes to gigabytes (GB):** divide by 1024 three times

### The main loop (read, send, sleep, repeat)

```python
while True:
    stats = get_stats()       # 1. READ the current stats
    api.send(APP, ENDPOINT, stats)  # 2. SEND them to the internet
    time.sleep(INTERVAL)      # 3. SLEEP for 60 seconds
    # Then the loop goes back to step 1 and REPEATs forever
```

The script follows a simple pattern:

1. **Read** -- gather all the stats from the Pi
2. **Send** -- push the stats to your meow meow scratch dashboard
3. **Sleep** -- wait 60 seconds (so we're not flooding the API)
4. **Repeat** -- go back to step 1

This runs forever until you press **Ctrl+C**. If sending fails (for example, your Wi-Fi drops), the script prints an error message but keeps running and tries again on the next cycle.

---

## Troubleshooting

### CPU temperature shows "N/A"

This is normal if you're not running on a Raspberry Pi. The temperature file (`/sys/class/thermal/thermal_zone0/temp`) only exists on devices with a thermal sensor that Linux knows about. On a regular laptop or desktop, this file usually isn't there, so the script shows N/A. On a real Pi, it should work automatically.

### "Permission denied" error

If you see a permission error, try running the script with `sudo`:

```bash
sudo python cpu_monitor.py
```

Some system files on Linux require administrator (root) access to read. On most Pis this isn't needed for the temperature file, but it can help if you've changed your Pi's security settings.

> **Note:** Don't forget to set your API key again when using `sudo`, since `sudo` starts a fresh environment. You can pass it inline like this:
>
> ```bash
> sudo MEOW_API_KEY="your-key" python cpu_monitor.py
> ```

### "ModuleNotFoundError: No module named 'psutil'"

This means the dependencies aren't installed yet. Run the install step again:

```bash
pip install -r requirements.txt
```

If you have multiple Python versions, make sure you're using the same one. Try:

```bash
pip3 install -r requirements.txt
python3 cpu_monitor.py
```

### Connection errors / "Send failed"

This usually means your Pi can't reach the internet. Check that:

1. **Your Pi is connected to Wi-Fi or Ethernet.** Try `ping google.com` in the terminal to test.
2. **Your API key is correct.** Double-check the key on your meow meow scratch dashboard.
3. **The meow meow scratch service is up.** Visit [meowmeowscratch.com](https://meowmeowscratch.com) in a browser to check.

The script won't crash on connection errors -- it will print "Send failed" and try again on the next cycle. So if your Wi-Fi blips for a moment, the monitor will recover on its own.

### "Set MEOW_API_KEY environment variable" and the script exits

You need to set your API key before running the script. See [Step 4](#4-set-your-api-key) above.
