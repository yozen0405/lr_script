import time
from core.system.logging.logger import log_msg
from core.actions.vision import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from core.actions.vision import get_main_stage_num
from core.base.exceptions import GameError
from scripts.shared.constants.positions import Positions
from scripts.shared.utils.retry import connection_retry
from typing import Optional
from scripts.shared.constants import Settlement, Battle, Confirm, MainView, Leonard, Retry
from scripts.shared.events.main_stage.enum import MainStageImg, Stages, Treasure
from scripts.shared.controller.context import GameContext

class MultiplierTutorialInterrupt:
    def __init__(self, context: GameContext):
        self.context = context

    def handle(self) -> bool:
        if not wait(self.context.serial, MainStageImg.MUTIPLIER_LOW_OFF_TEXT.value, timeout=2.0):
            return False
        wait_click(self.context.serial, Battle.CYCLE.value, wait_time=2.5)
        wait_click(self.context.serial, Leonard.BG_POINT.value, wait_time=2.5)
        wait_click(self.context.serial, MainStageImg.MUTIPLIER_LOW_OFF_TEXT.value, wait_time=1.0)
        wait_click(self.context.serial, MainStageImg.MUTIPLIER_LOW_ON_TEXT.value, wait_time=1.0)
        wait_click(self.context.serial, Leonard.BG_HAPPY.value, wait_time=1.0)
        return True