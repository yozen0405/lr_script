import os
import json
import threading
import time
import subprocess
from typing import List, Set

from core.system.adb.controller import AdbServerController
from core.system.logging.logger import log_msg

class AdbDeviceManager:
    """管理設備連線、發現與快取"""
    def __init__(self, adb_path: str, cache_file: str):
        self.adb_path = adb_path
        self.cache_file = cache_file
        if self.cache_file:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)

    def _load_cache(self) -> List[str]:
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _save_cache(self, connected_list: List[str]):
        try:
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(connected_list, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Cache write failed: {e}")

    def get_connected_devices(self) -> Set[str]:
        try:
            result = subprocess.run(
                [self.adb_path, "devices"],
                capture_output=True, text=True, timeout=5
            )
            lines = result.stdout.strip().splitlines()[1:]
            return set(line.split()[0] for line in lines if "\tdevice" in line)
        except Exception:
            return set()

    def connect(self, address: str) -> bool:
        try:
            result = subprocess.check_output(
                [self.adb_path, "connect", address], 
                stderr=subprocess.STDOUT,
                timeout=5
            )
            output = result.decode("utf-8", errors="ignore")
            result = "connected" in output or "already connected" in output
            return result
        except subprocess.CalledProcessError:
            return False
        except subprocess.TimeoutExpired:
            return False
        except KeyboardInterrupt:
            raise

    def restore_connections(self):
        for addr in self._load_cache():
            self.connect(addr)

    def scan_mumu(self, goal: int = 1, max_attempts: int = 10, base_port: int = 16416) -> List[str]:
        print(f"🔍 掃描 Mumu 模擬器 (目標: {goal})...")
        final_connected = []
        
        current = self.get_connected_devices()
        for addr in self._load_cache():
            if addr in current or self.connect(addr):
                final_connected.append(addr)
                print(f"快取中已在線: {addr}")
                if len(final_connected) >= goal: break
        
        if len(final_connected) >= goal:
            self._save_cache(final_connected)
            return final_connected

        for i in range(max_attempts):
            ports = [base_port, base_port + 1] if i == 0 else [base_port + i * 32]
            for port in ports:
                addr = f"127.0.0.1:{port}"
                if addr not in final_connected and self.connect(addr):
                    print(f"已連接: {addr}")
                    final_connected.append(addr)
                    if len(final_connected) >= goal:
                        self._save_cache(final_connected)
                        return final_connected
        
        self._save_cache(final_connected)
        return final_connected
    