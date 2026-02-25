# Pi CPU Monitor

Monitor your Raspberry Pi's system health — no extra hardware needed! Sends CPU temperature, CPU usage, memory, and disk stats to [meow meow scratch](https://meowmeowscratch.com).

Great for keeping tabs on headless Pis.

## Setup

```bash
pip install -r requirements.txt
export MEOW_API_KEY="your-key"
python cpu_monitor.py
```

## API setup

Create an app called `pi-cpu-monitor` with a collection endpoint `stats` and fields:

- `cpu_temp_c` (number)
- `cpu_percent` (number)
- `memory_percent` (number)
- `memory_used_mb` (number)
- `disk_percent` (number)
- `disk_used_gb` (number)
