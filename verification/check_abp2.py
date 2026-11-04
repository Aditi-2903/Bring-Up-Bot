"""Independent verification test for the ABP2DSNT001BD2A3XX on the Pi (I2C 0x28).

Reads the sensor over SSH, decodes it per the datasheet, and checks the answer key.
The agent cannot edit this file. Exit code 0 = PASS, 1 = FAIL.
    python verification/check_abp2.py
"""
import subprocess
import sys

ADDR = "0x28"                         # output type "2": I2C address 0x28
OUT_MIN, OUT_MAX = 1677722, 15099494  # transfer function "A": 10-90% of 2^24 counts
P_MIN, P_MAX = -1.0, 1.0              # range "001BD": +/-1 bar differential
CMD = (f"/usr/sbin/i2ctransfer -y 1 w3@{ADDR} 0xaa 0x00 0x00 && sleep 0.01 && "
       f"/usr/sbin/i2ctransfer -y 1 r7@{ADDR}")


def read_sensor() -> list[int]:
    r = subprocess.run(["ssh", "bringup-pi", CMD],
                       capture_output=True, text=True, timeout=20)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.strip() or "i2ctransfer failed")
    return [int(b, 16) for b in r.stdout.split()]


def main() -> int:
    try:
        data = read_sensor()
    except Exception as e:
        print(f"FAIL: no reading ({e})")
        return 1
    if len(data) != 7:
        print(f"FAIL: expected 7 bytes, got {data}")
        return 1

    status = data[0]
    p_counts = (data[1] << 16) | (data[2] << 8) | data[3]
    t_counts = (data[4] << 16) | (data[5] << 8) | data[6]
    pressure = (p_counts - OUT_MIN) * (P_MAX - P_MIN) / (OUT_MAX - OUT_MIN) + P_MIN
    temperature = t_counts * 200 / 16777215 - 50
    print(f"status=0x{status:02x} pressure_counts={p_counts} "
          f"pressure={pressure:+.4f} bar temperature={temperature:.2f} C")

    checks = {
        "powered (status bit 6 = 1)": bool(status & 0x40),
        "not busy (status bit 5 = 0)": not (status & 0x20),
        "memory integrity OK (status bit 2 = 0)": not (status & 0x04),
        "no math saturation (status bit 0 = 0)": not (status & 0x01),
        "pressure ~0 bar at room air (within +/-0.03 bar)": abs(pressure) <= 0.03,
        "temperature plausible (5 to 45 C)": 5 <= temperature <= 45,
    }
    for name, ok in checks.items():
        print(("PASS  " if ok else "FAIL  ") + name)
    passed = all(checks.values())
    print("RESULT:", "PASS" if passed else "FAIL")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
