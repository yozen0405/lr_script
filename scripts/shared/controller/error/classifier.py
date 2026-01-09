from enum import Enum, auto
from core.actions.vision import exist
from core.base.exceptions import AdbError
from scripts.shared.events.pre_stage.exception import PreStageTimeoutError
from core.system.emulator.exceptions import EmulatorRebootRequired
from scripts.shared.constants import GameView

class ErrorCategory(Enum):
    ADB = auto() # adb 網路不穩
    EMULATOR_REBOOT = auto() # 模擬器需要重啟
    INTERNAL = auto() # 遊戲內部錯誤，如彈窗、登入失敗等
    GAME = auto() # GameError
    FATAL = auto()

class ErrorClassifier:
    """負責分析 Exception 的類型"""
    
    @staticmethod
    def classify(e: Exception, serial: str) -> ErrorCategory:
        if isinstance(e, AdbError):
            return ErrorCategory.ADB
            
        if isinstance(e, PreStageTimeoutError):
            return ErrorCategory.INTERNAL
        
        if isinstance(e, EmulatorRebootRequired):
            return ErrorCategory.EMULATOR_REBOOT

        try:
            if exist(serial, GameView.ERROR_TEXT.value, threshold=0.9) or \
               exist(serial, GameView.AUTH_FAILED.value, threshold=0.9):
                return ErrorCategory.INTERNAL
        except Exception:
            pass

        return ErrorCategory.GAME