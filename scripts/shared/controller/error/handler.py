import logging
from typing import Dict, Type
from core.system.logging.reporter import AccountRunReporter
from core.base.exceptions import FatalError
from core.actions.system import log_msg, force_close_all_apps
from scripts.shared.controller.context import GameContext
from .classifier import ErrorClassifier, ErrorCategory
from .strategies.base import ErrorStrategy
from .strategies.implementations import (
    AdbErrorStrategy, 
    InternalErrorStrategy, 
    GameErrorStrategy,
    FatalErrorStrategy,
    EmulatorRebootStrategy
)

class RunErrorHandler:
    _STRATEGY_MAP: Dict[ErrorCategory, Type[ErrorStrategy]] = {
        ErrorCategory.ADB:      AdbErrorStrategy,
        ErrorCategory.INTERNAL: InternalErrorStrategy,
        ErrorCategory.GAME:   GameErrorStrategy,
        ErrorCategory.FATAL:    FatalErrorStrategy,
        ErrorCategory.EMULATOR_REBOOT: EmulatorRebootStrategy,
    }

    def __init__(self, context: GameContext, reporter: AccountRunReporter):
        self.ctx = context
        self.reporter = reporter
        self.serial = context.serial if context else "UNKNOWN"

    def handle(self, e: Exception) -> bool:
        """
        統一錯誤處理入口
        """
        category = ErrorClassifier.classify(e, self.serial)
        
        strategy_cls = self._STRATEGY_MAP.get(category, GameErrorStrategy)
        strategy = strategy_cls()

        self._apply_strategy(strategy, e)

        if self.ctx:
            if strategy.is_fatal(self.ctx) or self.ctx.retry_count >= 5:
                log_msg(self.serial, "錯誤策略判定為致命錯誤，終止任務", level=logging.CRITICAL)
                raise FatalError(f"Run Aborted by {category.name}")

        return False

    def _apply_strategy(self, strategy: ErrorStrategy, e: Exception):
        current_retry = 0
        if self.ctx and strategy.should_increment_retry():
            self.ctx.retry_count += 1
            current_retry = self.ctx.retry_count
            
        log_msg(
            self.serial, 
            f"[{strategy.__class__.__name__}] 處理異常: {e} (Retry: {current_retry})", 
            level=strategy.get_log_level()
        )

        if self.ctx and self.reporter:
            self.reporter.record(
                ctx=self.ctx,
                status=strategy.get_run_status(),
                error=e,
                take_screenshot=strategy.should_screenshot()
            )
        strategy.action(self.serial)