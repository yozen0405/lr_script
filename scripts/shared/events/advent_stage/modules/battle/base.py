from core.actions.vision.ocr.actions import get_text
from scripts.shared.controller.context import GameContext
from core.actions.vision import (
    wait_click, exist_click, exist, 
    wait, wait_vanish, drag, get_pos,
      check_region_brightness, get_all_pos,
      save_screenshot
)
from scripts.shared.events.advent_stage.modules.navigator.utils import StageNavigatorUtils
from scripts.shared.utils.retry import connection_retry
from scripts.shared.constants import Settlement, Confirm, Battle, MainView, Retry, Positions
from core.base.exceptions import GameError
from core.system.logging.logger import log_msg
from scripts.shared.events.advent_stage.enum import AdventImg, AdventStageName
from typing import Dict, Optional, Tuple
from scripts.shared.events.main_stage.enum import MainStageImg
from core.system.config import Config
from scripts.shared.constants import Leonard
from scripts.shared.events.advent_stage.modules.interrupt.tutorial import TutorialInterrupt 
from scripts.shared.events.advent_stage.session import AdventStageSession
import time

class StageBattle:
    def __init__(self, context: GameContext, session: AdventStageSession):
        self.ctx = context
        self.session = session

    def run(self):
        self.session.lose = False

        start_time = time.time()
        while time.time() - start_time < 120:
            if self.session.repeat > 1 and exist(self.ctx.serial, Battle.LOOP_END_TEXT.value, threshold=0.9):
                break

            if self.session.repeat == 1 and exist_click(self.ctx.serial, Settlement.TEXT.value, threshold=0.9):
                break

            if exist(self.ctx.serial, Retry.TEXT1.value):
                exist_click(self.ctx.serial, Retry.BTN.value)

        raise GameError("戰鬥超時")