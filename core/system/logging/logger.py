import logging
from collections import deque
from datetime import datetime
from typing import Dict, List
from core.system.config import Config

LOG_IMPORTANT = 25
logging.addLevelName(LOG_IMPORTANT, "EVENT")

class GameLogger:
    _instances: Dict[str, 'GameLogger'] = {}

    def __new__(cls, serial: str):
        if serial not in cls._instances:
            instance = super().__new__(cls)
            instance._init_logger(serial)
            cls._instances[serial] = instance
        return cls._instances[serial]

    def _init_logger(self, serial: str):
        self.serial = serial
        self.history = deque(maxlen=500) 
        self.debug_mode = Config().get_is_debug()
        
        self.logger = logging.getLogger(f"Game_{serial}")
        
        if self.debug_mode:
            self.logger.setLevel(logging.INFO)
        else:
            self.logger.setLevel(LOG_IMPORTANT)
        
        if not self.logger.handlers:
            formatter = logging.Formatter(f'[%(asctime)s][{serial}][%(levelname)s] %(message)s', '%H:%M:%S')
            
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

    def log(self, msg: str, level=logging.INFO):
        timestamp = datetime.now().strftime('%H:%M:%S')
        formatted_msg = f"[{timestamp}] {msg}"
        
        self.history.append(formatted_msg)
        
        self.logger.log(level, msg)

    def get_recent_logs(self) -> List[str]:
        """調閱最近 10 筆紀錄"""
        return list(self.history)

    def get_traceback_str(self) -> str:
        """獲取最近紀錄的字串格式 (例如用於報錯時回報內容)"""
        return "\n".join(self.history)


def log_msg(serial: str, msg: str, level=logging.INFO):
    GameLogger(serial).log(msg, level)

def log_event(serial: str, msg: str):
    log_msg(serial, msg, level=LOG_IMPORTANT)