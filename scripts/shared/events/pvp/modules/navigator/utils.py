from scripts.shared.controller.context import GameContext
from core.actions.vision import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from scripts.shared.utils.retry import connection_retry
from scripts.shared.constants import Settlement, Confirm, Battle, MainView, Retry, Positions
from core.base.exceptions import GameError
from core.system.logging.logger import log_msg
from typing import Optional, Tuple
from core.system.config import Config
from scripts.shared.constants import Leonard
from scripts.shared.events.pvp.enum import PvPImg
import time

class StageNavigatorUtils:
    def __init__(self, context: GameContext):
        self.ctx = context

    def _attempt_enter(self):
        if exist(self.ctx.serial, PvPImg.TEXT.value):
            return
        
        for _ in range(3):
            if exist_click(self.ctx.serial, PvPImg.BTN.value):
                connection_retry(self.ctx.serial, vanish=[(PvPImg.BTN.value, 0.9)], timeout=50.0)
                return
            else:
                drag(self.ctx.serial, (600, 300), (150, 300), wait_time=1.5)

        raise GameError("無法進入降臨關卡")