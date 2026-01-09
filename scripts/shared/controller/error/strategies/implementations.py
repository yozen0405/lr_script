import logging
from core.actions.system import force_close_all_apps
from core.base.exceptions import FatalError
from core.system.logging.reporter import RunStatus
from scripts.shared.controller.context import GameContext
from core.system.emulator import get_emulator_controller
from .base import ErrorStrategy

class AdbErrorStrategy(ErrorStrategy):
    def should_increment_retry(self) -> bool:
        return True

    def get_run_status(self) -> RunStatus:
        return RunStatus.ERROR

    def should_screenshot(self) -> bool:
        return False

    def is_fatal(self, context: GameContext) -> bool:
        return False

    def get_log_level(self) -> int:
        return logging.ERROR
    
    def action(self, serial: str):
        force_close_all_apps(serial)

class InternalErrorStrategy(ErrorStrategy):
    def should_increment_retry(self) -> bool:
        return False 

    def get_run_status(self) -> RunStatus:
        return RunStatus.WARNING

    def should_screenshot(self) -> bool:
        return False

    def is_fatal(self, context: GameContext) -> bool:
        return False

    def get_log_level(self) -> int:
        return logging.INFO
    
    def action(self, serial: str):
        force_close_all_apps(serial)

class GameErrorStrategy(ErrorStrategy):
    def should_increment_retry(self) -> bool:
        return True

    def get_run_status(self) -> RunStatus:
        return RunStatus.ERROR

    def should_screenshot(self) -> bool:
        return True 

    def is_fatal(self, context: GameContext) -> bool:
        return False

    def get_log_level(self) -> int:
        return logging.ERROR
    
    def action(self, serial: str):
        force_close_all_apps(serial)

class FatalErrorStrategy(ErrorStrategy):
    def should_increment_retry(self) -> bool:
        return False
    def get_run_status(self) -> RunStatus:
        return RunStatus.ABORTED
    def should_screenshot(self) -> bool:
        return True
    def is_fatal(self, context: GameContext) -> bool:
        return True
    def get_log_level(self) -> int:
        return logging.CRITICAL
    
    def action(self, serial: str):
        force_close_all_apps(serial)

class EmulatorRebootStrategy(ErrorStrategy):
    def should_increment_retry(self) -> bool:
        return False

    def get_run_status(self) -> RunStatus:
        return RunStatus.ERROR

    def should_screenshot(self) -> bool:
        return False

    def is_fatal(self, context: GameContext) -> bool:
        return False

    def get_log_level(self) -> int:
        return logging.ERROR
    
    def action(self, serial: str):
        controller = get_emulator_controller()
        if not controller.restart(serial):
            raise FatalError("模擬器重啟失敗，無法繼續執行")