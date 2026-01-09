import os
import csv
import threading
import traceback
from datetime import datetime
from enum import Enum
from typing import Dict, Optional
from core.actions.vision import save_screenshot
from core.system.logging.logger import log_msg
from scripts.shared.controller.context import GameContext

class RunStatus(Enum):
    RUNNING = "Running"
    SUCCESS = "Success"
    WARNING = "Warning"
    ERROR = "Error"
    ABORTED = "Aborted"

class AccountRunReporter:
    _instances = {}
    _file_lock = threading.Lock()

    def __new__(cls, serial: str):
        if serial not in cls._instances:
            instance = super().__new__(cls)
            instance._init_session(serial)
            cls._instances[serial] = instance
        return cls._instances[serial]

    def _init_session(self, serial: str):
        self.serial = serial
        self.log_dir = "./bin/logs"
        self.snapshot_dir = os.path.join(self.log_dir, "snapshots")
        self.summary_file = os.path.join(self.log_dir, "summary_results.csv")
        os.makedirs(self.snapshot_dir, exist_ok=True)
        self._init_csv_header()

    def _init_csv_header(self):
        headers = ["Serial", "Start", "End", "Status", "Rangers", "Retries", "Error", "Snapshot"]
        if not os.path.exists(self.summary_file):
            with self._file_lock:
                with open(self.summary_file, 'w', newline='', encoding='utf-8') as f:
                    csv.DictWriter(f, fieldnames=headers).writeheader()

    def record(self, ctx: GameContext, status: RunStatus, error: Exception | str = None, take_screenshot: bool = True):
        end_time = datetime.now()
        snapshot_path = "N/A"

        if status == RunStatus.SUCCESS:
            ctx.last_error_msg = ""
        
        if status != RunStatus.SUCCESS:
            ctx.last_error_msg = str(error) if error else "Unknown Error"
            if take_screenshot:
                snapshot_path = self._save_debug_artifacts(ctx, error)

        self._write_to_summary(ctx, status, end_time, snapshot_path)

    def record_system_error(self, serial: str, error: Exception | str):
        temp_ctx = GameContext(serial=serial)
        temp_ctx.start_time = datetime.now()
        temp_ctx.last_error_msg = str(error)
        self.record(temp_ctx, RunStatus.ERROR, error, take_screenshot=True)

    def _save_debug_artifacts(self, ctx: GameContext, error: Exception | str) -> str:
        """
        核心保存邏輯：生成截圖與詳細的 .txt 報告
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        clean_serial = self.serial.replace(".", "_").replace(":", "_")
        name_base = f"err_{timestamp}_{clean_serial}"
        
        img_path = os.path.join(self.snapshot_dir, f"{name_base}.png")
        report_path = os.path.join(self.snapshot_dir, f"{name_base}.txt")

        try:
            save_screenshot(self.serial, img_path)
        except Exception as e:
            log_msg(self.serial, f"[AccountRunReporter] 截圖失敗: {e}")
            img_path = "Screenshot Failed"

        try:
            from core.system.logging.logger import GameLogger
            recent_logs = GameLogger(self.serial).get_traceback_str()
            
            trace_info = traceback.format_exc() if isinstance(error, Exception) else "N/A (Str Error)"

            with open(report_path, "w", encoding="utf-8") as f:
                f.write(f"=== Run Error Report ===\n")
                f.write(f"Time: {datetime.now()}\n")
                f.write(f"Serial: {self.serial}\n")
                f.write(f"Status: {ctx.last_error_msg}\n\n")
                
                f.write(f"=== GameLogger Recent Logs ===\n")
                f.write(recent_logs if recent_logs else "No logs found.")
                
                f.write(f"\n\n=== Python Traceback ===\n")
                f.write(trace_info)
                
            return img_path
        except Exception as e:
            print(f"[AccountRunReporter] Artifact save failed: {e}")
            return "Failed to save"

    def _write_to_summary(self, ctx: GameContext, status: RunStatus, end_time: datetime, snapshot_path: str):
        """
        將 GameContext 的內容持久化到 CSV
        """
        data = {
            "Serial": ctx.serial,
            "Start": ctx.start_time.strftime("%m-%d %H:%M:%S"),
            "End": end_time.strftime("%H:%M:%S"),
            "Status": status.value,
            "Rangers": "+".join(ctx.pulled_rangers) if ctx.pulled_rangers else "None",
            "Retries": ctx.retry_count,
            "Error": ctx.last_error_msg or "None",
            "Snapshot": snapshot_path
        }
        
        with self._file_lock:
            with open(self.summary_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=list(data.keys()))
                writer.writerow(data)