from abc import ABC, abstractmethod

class EmulatorController(ABC):
    """模擬器控制器的抽象基類"""
    
    @abstractmethod
    def restart(self, serial: str) -> bool:
        pass