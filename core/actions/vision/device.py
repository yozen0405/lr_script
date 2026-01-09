import uiautomator2 as u2
import concurrent.futures
import atexit
import cv2
import numpy as np
from typing import Optional, Dict
from core.system.adb import adb_cmd
from core.system.logging.logger import log_msg
from core.base.exceptions import AdbError

class DeviceController:
    """負責與 Android 設備的底層通訊"""
    
    def __init__(self, serial: str):
        self.serial = serial
        self.d = u2.connect(serial)
        self.d.implicitly_wait(0.0)
        
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        atexit.register(self.shutdown)

    def shutdown(self):
        self.executor.shutdown(wait=False)

    def _connect_worker(self):
        d = u2.connect(self.serial)
        d.implicitly_wait(0.0)
        return d

    def reconnect(self):
        log_msg(self.serial, "偵測到連線中斷，嘗試重新連接 u2...")
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as temp_exec:
                future = temp_exec.submit(self._connect_worker)
                self.d = future.result(timeout=5.0)
            log_msg(self.serial, "u2 重新連接成功！")
        except Exception as e:
            log_msg(self.serial, f"u2 重連失敗: {e}, 將使用 ADB 備援")

    def screenshot(self) -> np.ndarray:
        """嘗試高速截圖，失敗則退回 ADB"""
        # 1. U2 Fast Screenshot
        try:
            future = self.executor.submit(lambda: self.d.screenshot(format='opencv'))
            image = future.result(timeout=3.0)
            if image is not None: return image
        except KeyboardInterrupt:
            raise
        except Exception as e:
            # log_msg(self.serial, f"高速截圖失效: {e}")
            self.reconnect()

        # 2. ADB Fallback
        return self._adb_screenshot_fallback()

    def _adb_screenshot_fallback(self) -> np.ndarray:
        try:
            result = adb_cmd(
                self.serial, ["exec-out", "screencap", "-p"], 
                timeout=3, silent=True, binary=True
            )
            if result and result.stdout:
                buf = np.frombuffer(result.stdout, np.uint8)
                return cv2.imdecode(buf, cv2.IMREAD_COLOR)
        except Exception:
            pass
        
        raise AdbError(f"[{self.serial}] 截圖完全失敗")

    def click(self, x: int, y: int):
        try:
            self.d.click(x, y)
        except Exception:
            adb_cmd(self.serial, ["shell", "input", "tap", str(x), str(y)], silent=True)

    def drag(self, x1, y1, x2, y2, duration=300):
        adb_cmd(self.serial, ["shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration)], silent=True)
        
    def get_current_app(self) -> Dict[str, str]:
        try:
            return self.d.app_current()
        except Exception:
            return {}
        
    def input_keyevent(self, key_code: int):
        adb_cmd(self.serial, ["shell", "input", "keyevent", str(key_code)], silent=True)