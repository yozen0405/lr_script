from abc import ABC, abstractmethod
from enum import Enum

class BaseStrategy(ABC):
    def __init__(self, serial):
        self.serial = serial

    @abstractmethod
    def check(self) -> bool:
        """
        看是不是在自己這個狀態
        """
        pass

    def proccess(self):
        """
        處理這個狀態
        """
        pass