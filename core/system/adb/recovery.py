import time
import subprocess
import threading
from enum import Enum, auto
from core.system.logging.logger import log_msg
from .controller import AdbServerController
from .device import AdbDeviceManager
from core.system.emulator import get_emulator_controller
from typing import Union, Tuple
from dataclasses import dataclass
from core.system.emulator.exceptions import EmulatorRebootRequired

class AdbFailureType(Enum):
    NONE = auto()
    DAEMON_CRASH = auto()
    DEVICE_OFFLINE = auto()
    TRANSPORT_ERROR = auto()
    UNAUTHORIZED = auto()
    TIMEOUT = auto()
    UNKNOWN_ERROR = auto()

class AdbRecoveryStrategy:
    def __init__(self, adb_path: str, server: AdbServerController, devices: AdbDeviceManager):
        self.adb_path = adb_path
        self.server = server
        self.devices = devices
        self.emulator = get_emulator_controller() 
        self._lock = threading.Lock()

    def handle_error(
        self,
        serial: str,
        raw_stderr: Union[str, bytes, None],
        attempt: int,
        binary: bool
    ) -> Tuple[bool, str]:
        error_msg = self._decode_stderr(raw_stderr, binary)
        failure_type = self._diagnose(error_msg)

        return self._recover(serial, failure_type, attempt, error_msg)

    def handle_timeout(self, serial: str, attempt: int) -> Tuple[bool, str]:
        return self._recover(serial, AdbFailureType.TIMEOUT, attempt, "Command Timeout")
    
    def _recover(self, serial: str, failure_type: AdbFailureType, attempt: int, error_msg: str) -> Tuple[bool, str]:
        if failure_type == AdbFailureType.NONE:
            return False, error_msg

        if failure_type in (AdbFailureType.DAEMON_CRASH, AdbFailureType.TIMEOUT):
            if attempt == 0:
                self._soft_reconnect(serial)
                return True, error_msg
            self._global_restart(serial)
            return True, error_msg

        if failure_type == AdbFailureType.UNAUTHORIZED:
            if attempt == 0:
                self._soft_reconnect(serial)
                return True, error_msg
            self._global_restart(serial)
            return True, error_msg

        if failure_type in (AdbFailureType.DEVICE_OFFLINE, AdbFailureType.TRANSPORT_ERROR):
            if attempt == 0:
                log_msg(serial, "Recovery L1: Soft Reconnect")
                self._soft_reconnect(serial)
                return True, error_msg

            if attempt == 1:
                log_msg(serial, "Recovery L2: Restart ADB Server")
                self._global_restart(serial)
                return True, error_msg

            log_msg(serial, "Recovery L3: Hard Emulator Restart")
            raise EmulatorRebootRequired(f"Emulator reboot required due to ADB failure: {error_msg}")

        if attempt >= 1:
            self._global_restart(serial)
            return True, error_msg

        return True, error_msg

    def _decode_stderr(self, raw_err, binary: bool) -> str:
        if not raw_err: return ""
        if binary and isinstance(raw_err, bytes):
            return raw_err.decode('utf-8', errors='ignore').strip()
        if isinstance(raw_err, str):
            return raw_err.strip()
        return str(raw_err).strip()
    
    def _diagnose(self, stderr: str) -> AdbFailureType:
        err = stderr.lower()

        if any(x in err for x in [
            "daemon not running",
            "cannot connect to daemon",
            "could not read ok",
            "adb server version"
        ]):
            return AdbFailureType.DAEMON_CRASH

        if "unauthorized" in err:
            return AdbFailureType.UNAUTHORIZED

        if any(x in err for x in [
            "offline",
            "device offline",
            "not found",
            "no devices"
        ]):
            return AdbFailureType.DEVICE_OFFLINE

        if any(x in err for x in [
            "broken pipe",
            "connection reset",
            "transport",
            "closed"
        ]):
            return AdbFailureType.TRANSPORT_ERROR

        return AdbFailureType.UNKNOWN_ERROR

    def _soft_reconnect(self, serial: str) -> bool:
        subprocess.run([self.adb_path, "disconnect", serial], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(0.5)
        self.devices.connect(serial)
        return serial in self.devices.get_connected_devices()

    def _global_restart(self, serial: str):
        with self._lock:
            self.server.restart(serial)
            self.devices.restore_connections()

    def _emulator_reboot(self, serial: str) -> bool:
        success = self.emulator.restart(serial)
        if success:
            self.devices.connect(serial)
        return success