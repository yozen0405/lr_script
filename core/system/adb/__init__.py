import os
import threading
from typing import List
import subprocess
from core.system.adb.health import EmulatorHealthMonitor
from core.system.emulator import get_emulator_controller

from .controller import AdbServerController
from .device import AdbDeviceManager
from .executor import AdbCommandExecutor
from .recovery import AdbRecoveryStrategy

class AdbManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(AdbManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False): return
        
        self.adb_path = os.path.join("bin", "adb", "adb.exe")
        self.cache_file = os.path.join("bin", "cache.json")
        
        self.server = AdbServerController(self.adb_path)
        self.devices = AdbDeviceManager(self.adb_path, self.cache_file)
        self.recovery_strategy = AdbRecoveryStrategy(self.adb_path, self.server, self.devices)
        self.executor = AdbCommandExecutor(self.adb_path, self.server, self.recovery_strategy)
        self.health_monitor = EmulatorHealthMonitor(self.adb_path)
        
        self._initialized = True

    def execute(self, *args, **kwargs):
        return self.executor.execute(*args, **kwargs)

    def scan_mumu(self, *args, **kwargs):
        return self.devices.scan_mumu(*args, **kwargs)
    
    def heartbeat(self, serial: str):
        self.health_monitor.heartbeat(serial)

adb_manager = AdbManager()

def adb_cmd(serial: str, args: List[str], timeout: int = 15, silent: bool = False, binary: bool = False):
    return adb_manager.execute(serial, args, timeout=timeout, retries=1, silent_log=silent, binary=binary)

def connect_all_mumu_instances(goal=1, max_attempts=10, base_port=16416):
    return adb_manager.scan_mumu(goal, max_attempts, base_port)

def heartbeat(serial: str):
    adb_manager.heartbeat(serial)