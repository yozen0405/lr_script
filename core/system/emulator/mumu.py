import subprocess
import time
import os
from typing import Optional
from core.system.logging.logger import log_msg
from .base import EmulatorController
import subprocess
import time
import os
import threading
from typing import Optional, Dict
from core.system.logging.logger import log_msg
from .base import EmulatorController

class MuMuController(EmulatorController):
    _pool_guard = threading.Lock()
    _index_locks: Dict[int, threading.Lock] = {}

    def __init__(self, adb_path: str = None):
        self.manager_path = r"D:\Programs\MuMuPlayerGlobal-12.0\nx_main\MuMuManager.exe"
        self.adb_path = adb_path or os.path.join("bin", "adb", "adb.exe")
        if not os.path.exists(self.manager_path):
            raise FileNotFoundError(f"MuMuManager 路徑不存在: {self.manager_path}")

    @classmethod
    def _get_index_lock(cls, index: int) -> threading.Lock:
        with cls._pool_guard:
            lock = cls._index_locks.get(index)
            if lock is None:
                lock = threading.Lock()
                cls._index_locks[index] = lock
            return lock

    def restart(self, serial: str) -> bool:
        index = self._serial_to_index(serial)
        if index is None:
            log_msg(serial, "無法解析 Index，跳過模擬器重啟")
            return False

        lock = self._get_index_lock(index)

        acquired = lock.acquire(timeout=5)
        if not acquired:
            log_msg(serial, f"Index {index} 正在重啟中，跳過本次重啟")
            return False

        try:
            log_msg(serial, f"正在執行模擬器硬重啟... (index={index})")

            self._run_manager_cmd(["control", "-v", str(index), "restart"], serial)

            if self._wait_for_boot(serial, timeout=60):
                log_msg(serial, "模擬器啟動完成")
                return True
            else:
                log_msg(serial, "模擬器啟動超時")
                return False

        except Exception as e:
            log_msg(serial, f"模擬器重啟流程異常: {e}")
            return False
        finally:
            lock.release()

    def _wait_for_boot(self, serial: str, timeout: int) -> bool:
        start = time.time()
        log_msg(serial, "等待 Android 系統載入...")
        down_deadline = start + min(20, timeout)

        while time.time() < down_deadline:
            if self._is_boot_completed(serial) is False:
                log_msg(serial, "已偵測到重啟開始（設備暫時不可用）")
                break
            time.sleep(0.5)

        while time.time() - start < timeout:
            if self._is_boot_completed(serial) is True:
                return True
            time.sleep(2)

        log_msg(serial, "模擬器啟動超時")
        return False

    def _serial_to_index(self, serial: str) -> Optional[int]:
        try:
            if "127.0.0.1:" not in serial: return None
            port = int(serial.split(":")[1])
            if port < 16384: return None
            return (port - 16384) // 32
        except Exception:
            return None
        
    def _is_boot_completed(self, serial: str) -> Optional[bool]:
        try:
            r = subprocess.run(
                [self.adb_path, "-s", serial, "shell", "getprop", "sys.boot_completed"],
                capture_output=True, text=True, timeout=3
            )

            if r.returncode != 0:
                return False

            return r.stdout.strip() == "1"

        except subprocess.TimeoutExpired:
            return False
        except Exception:
            return False

    # def _run_manager_cmd(self, args: list):
        # subprocess.run(
        #     [self.manager_path] + args,
        #     check=True,
        #     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        # )

    def _run_manager_cmd(self, args: list, serial: str):
        try:
            subprocess.run(
                [self.manager_path] + args,
                check=True,
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
            out = (e.stdout or "").strip()
            err = (e.stderr or "").strip()
            log_msg(serial, f"Manager cmd failed: {[self.manager_path] + args}")
            if out:
                log_msg(serial, f"Manager stdout: {out}")
            if err:
                log_msg(serial, f"Manager stderr: {err}")
            raise
