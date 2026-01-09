from abc import ABC, abstractmethod
from core.system.logging.reporter import RunStatus
from scripts.shared.controller.context import GameContext

class ErrorStrategy(ABC):
    """錯誤處理策略的基類"""

    @abstractmethod
    def should_increment_retry(self) -> bool:
        pass

    @abstractmethod
    def get_run_status(self) -> RunStatus:
        pass

    @abstractmethod
    def should_screenshot(self) -> bool:
        pass

    @abstractmethod
    def is_fatal(self, context: GameContext) -> bool:
        pass
    
    @abstractmethod
    def get_log_level(self) -> int:
        pass

    @abstractmethod
    def action(self, serial: str):
        pass