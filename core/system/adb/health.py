import time
import subprocess
from typing import Optional
from core.system.emulator.exceptions import EmulatorRebootRequired
from core.system.logging.logger import log_msg

class EmulatorHealthMonitor:
    def __init__(self, adb_path: str):
        self.adb_path = adb_path
        self.ram_threshold_mb = 2500
        self._last_check: dict[str, float] = {}

    def heartbeat(self, serial: str):
        now = time.time()
        last = self._last_check.get(serial, 0.0)
        if now - last < 10.0:
            return
        self._last_check[serial] = now

        used_mb = self._get_ram_used_mb(serial)
        if used_mb is None:
            return
        log_msg(serial, f"目前 RAM 使用量: {used_mb} MB")

        if used_mb >= self.ram_threshold_mb:
            raise EmulatorRebootRequired(f"RAM too high: {used_mb} MB >= {self.ram_threshold_mb} MB")

    def _get_ram_used_mb(self, serial: str):
        try:
            r = subprocess.run(
                [self.adb_path, "-s", serial, "shell", "cat", "/proc/meminfo"],
                capture_output=True, text=True, timeout=3
            )
            if r.returncode != 0:
                return None

            # MemTotal/MemAvailable: kB
            total_kb = None
            avail_kb = None
            for line in r.stdout.splitlines():
                if line.startswith("MemTotal:"):
                    total_kb = int(line.split()[1])
                elif line.startswith("MemAvailable:"):
                    avail_kb = int(line.split()[1])

            if total_kb is None or avail_kb is None:
                return None

            used_kb = total_kb - avail_kb
            return used_kb // 1024
        except Exception:
            return None
