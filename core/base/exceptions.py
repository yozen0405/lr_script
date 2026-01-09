class AutomationError(Exception):
    """所有自動化腳本的基類錯誤"""
    pass

# --- Level 1: Recoverable ---
class RecoverableError(AutomationError):
    pass

class GameError(RecoverableError):
    """遊戲邏輯錯誤 (如: 找不到按鈕、卡在某個畫面)"""
    pass

class AdbError(RecoverableError):
    """ADB 執行相關的通用錯誤"""
    pass

# --- Level 2: Fatal ---
# 這類錯誤代表：重啟也沒救，可能是 Code 寫錯、設定檔遺失、硬碟滿了
class FatalError(AutomationError):
    pass

class ConfigError(FatalError):
    pass