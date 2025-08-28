from abc import ABC, abstractmethod

class BasePhase(ABC):
    def __init__(self, serial):
        self.serial = serial

    @abstractmethod
    def steps(self):
        """子類必須回傳一個 list[callable]"""
        pass

    def _detect_event(self) -> int:
        return 0

    def run(self, start_idx: int | None = None):
        idx = self._detect_event() if start_idx is None else start_idx
        s = self.steps()
        while idx < len(s):
            s[idx]()
            idx += 1
