#!/usr/bin/env python3
"""ABP2 pressure reader: the "product app" running on the Pi.

Reads settings from config.json next to this file, talks to the sensor over I2C
using only the standard library, and prints one reading. Seeded bugs break
config.json; Bring-Up Bot must diagnose and fix them.
    python3 ~/abp2_app/read_pressure.py
"""
import fcntl
import json
import os
import sys
import time
from pathlib import Path

I2C_SLAVE = 0x0703          # Linux ioctl: set the target device address
MEASURE_CMD = bytes([0xAA, 0x00, 0x00])

cfg = json.loads((Path(__file__).with_name("config.json")).read_text())
bus = cfg["i2c_bus"]
address = int(cfg["i2c_address"], 16)
dev = f"/dev/i2c-{bus}"

try:
    fd = os.open(dev, os.O_RDWR)
except OSError as e:
    sys.exit(f"ERROR: cannot open {dev} ({e.strerror})")

try:
    fcntl.ioctl(fd, I2C_SLAVE, address)
    os.write(fd, MEASURE_CMD)
    time.sleep(cfg["conversion_wait_ms"] / 1000)
    data = os.read(fd, 7)
except OSError as e:
    sys.exit(f"ERROR: no response from address {cfg['i2c_address']} on {dev} ({e.strerror})")
finally:
    os.close(fd)

status = data[0]
p_counts = int.from_bytes(data[1:4], "big")
t_counts = int.from_bytes(data[4:7], "big")
pressure = ((p_counts - cfg["output_min_counts"])
            * (cfg["pressure_max_bar"] - cfg["pressure_min_bar"])
            / (cfg["output_max_counts"] - cfg["output_min_counts"])
            + cfg["pressure_min_bar"])
temperature = t_counts * 200 / 16777215 - 50

if status & 0x20:
    print(f"WARNING: sensor busy (status=0x{status:02x}); data may be stale")
print(f"pressure={pressure:+.4f} bar temperature={temperature:.2f} C "
      f"status=0x{status:02x} raw_counts={p_counts}")
