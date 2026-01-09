import subprocess
import time
from core.system.logging.logger import log_msg
from core.base.exceptions import AdbError
import threading

class AdbServerController:
    """管理 ADB Server Process 的生命週期"""
    def __init__(self, adb_path: str):
        self.adb_path = adb_path
        self.last_restart_time = 0.0
        self._lock = threading.Lock()   
        self._restarting = False
        self._done = threading.Event()
        self._done.set()

    def is_restarting(self) -> bool:
        return self._restarting

    def wait_until_ready(self, timeout: float = 8.0) -> bool:
        return self._done.wait(timeout=timeout)

    def start(self, serial: str, timeout: int = 10) -> bool:
        try:
            subprocess.run(
                [self.adb_path, "start-server"],
                check=True, timeout=timeout,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            time.sleep(2)
            return True
        except Exception as e:
            log_msg(serial, f"Start Server Failed: {e}")
            return False

    def stop(self, serial: str, timeout: int = 5):
        try:
            subprocess.run(
                [self.adb_path, "kill-server"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                timeout=timeout
            )
            time.sleep(0.5)
        except subprocess.TimeoutExpired:
            pass
        
        subprocess.run(["taskkill", "/F", "/IM", "adb.exe", "/T"], 
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1)

    def restart(self, serial: str):
        with self._lock:
            now = time.time()
            if now - self.last_restart_time < 10.0:
                log_msg(serial, "ADB Server 最近已重啟過，跳過本次重啟請求")
                return

            self.last_restart_time = now
            self._restarting = True
            self._done.clear()

            try:
                log_msg(serial, "Restarting ADB Server")
                self.stop(serial)
                if self.start(serial):
                    log_msg(serial, "ADB Server Restarted")
                else:
                    raise AdbError("ADB Restart Failed")
            finally:
                self._restarting = False
                self._done.set()