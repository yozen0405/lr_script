from abc import ABC, abstractmethod
from scripts.shared.controller.context import GameContext

class StateResolver(ABC):
    @abstractmethod
    def resolve(self, context: GameContext) -> None:
        """執行解決方案"""
        pass