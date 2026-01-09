from scripts.shared.controller.context import GameContext
from core.actions.vision import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from scripts.shared.utils.retry import connection_retry
from scripts.shared.constants import Settlement, Confirm, Battle, MainView, Retry, Positions
from core.base.exceptions import GameError
from core.system.logging.logger import log_msg
from scripts.shared.events.advent_stage.enum import AdventImg, AdventStageName
from typing import Optional, Tuple
from scripts.shared.events.main_stage.enum import MainStageImg
from core.system.config import Config
from scripts.shared.constants import Leonard
from scripts.shared.events.advent_stage.modules.interrupt.tutorial import TutorialInterrupt
import time

class StageNavigatorUtils:
    def __init__(self, context: GameContext):
        self.ctx = context

    def _attempt_enter(self):
        if exist(self.ctx.serial, AdventImg.TEXT.value):
            return
        
        for _ in range(3):
            if exist_click(self.ctx.serial, AdventImg.BTN.value):
                try:
                    connection_retry(self.ctx.serial, vanish=[(AdventImg.TEXT.value, 0.9)], timeout=50.0)
                except GameError:
                    continue
                return
            elif exist(self.ctx.serial, MainStageImg.BTN.value):
                drag(self.ctx.serial, (600, 300), (150, 300), wait_time=1.5)

        raise GameError("無法進入降臨關卡")
    
    def _handle_pre_anime(self):
        for _ in range(7):
            if exist(self.ctx.serial, AdventImg.TEXT.value):
                break
            if not exist_click(self.ctx.serial, Battle.ANIME.value, threshold=0.85, wait_time=1.5):
                time.sleep(1.0)