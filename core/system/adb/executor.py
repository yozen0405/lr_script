import subprocess
import time
from typing import List
from core.system.logging.logger import log_msg
from core.base.exceptions import AdbError
from .recovery import AdbRecoveryStrategy
from .controller import AdbServerController

class AdbCommandExecutor:
    def __init__(self, adb_path: str, server: AdbServerController, recovery_strategy: AdbRecoveryStrategy):
        self.adb_path = adb_path
        self.server = server
        self.recovery = recovery_strategy

    def execute(self, serial: str, args: List[str], timeout: int = 15, retries: int = 5, silent_log: bool = False, binary: bool = False) -> subprocess.CompletedProcess:
        last_error_msg = "Unknown"

        for attempt in range(retries + 1):
            if self.server.is_restarting():
                self.server.wait_until_ready()

            try:
                result = subprocess.run(
                    [self.adb_path, "-s", serial] + args,
                    capture_output=True, text=not binary, timeout=timeout
                )
                
                if result.returncode == 0:
                    return result
                
                if result.returncode == 3221225786:
                    raise KeyboardInterrupt("偵測到強制終止訊號")
                
                should_retry, last_error_msg = self.recovery.handle_error(
                    serial, result.stderr, attempt, binary
                )

                if not silent_log:
                    log_msg(serial, f"ADB Error ({attempt+1}/{retries+1}): {last_error_msg}")

                if not should_retry or attempt == retries:
                    break

                time.sleep(1)

            except subprocess.TimeoutExpired:
                should_retry, last_error_msg = self.recovery.handle_timeout(serial, attempt)
                
                if not silent_log:
                    log_msg(serial, f"ADB Timeout ({attempt+1}/{retries+1})")

                if not should_retry or attempt == retries:
                    break

                time.sleep(1)

            except Exception as e:
                last_error_msg = str(e)
                time.sleep(1)

        raise AdbError(f"ADB Cmd Failed: {' '.join(args)} | Error: {last_error_msg}")