import time
from core.actions.vision import check_region_brightness
from core.system.logging.logger import log_msg
from core.actions.vision import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from core.base.exceptions import GameError
from scripts.shared.constants.positions import Positions
from scripts.shared.controller.context import GameContext
from scripts.shared.events.pvp.session import StageSession
from scripts.shared.utils.retry import connection_retry
from typing import Optional
from scripts.shared.constants import Settlement, Battle, Confirm, MainView, Leonard, Retry
from scripts.shared.events.pvp.enum import PvPImg

class StageFinder:
    def __init__(self, context: GameContext, session: StageSession):
        self.ctx = context
        self.session = session

    def enter_stage(self):
        start_time = time.time()
        found = False
        while time.time() - start_time < 120.0:
            if exist(self.ctx.serial, Retry.TEXT1.value):
                exist_click(self.ctx.serial, Retry.BTN.value)

            if exist_click(self.ctx.serial, PvPImg.BATTLE.value):
                pass

            if exist(self.ctx.serial, PvPImg.MATCHING_TEXT.value, threshold=0.8):
                wait_click(self.ctx.serial, PvPImg.CHALLENGE.value)
                found = True

            if exist(self.ctx.serial, PvPImg.BLIND_MATCH.value, threshold=0.8):
                wait_click(self.ctx.serial, PvPImg.CHALLENGE.value)
                found = True

            if found:
                if exist(self.ctx.serial, PvPImg.PRE_START_PAGE.value, threshold=0.9):
                    return
        raise GameError("無法進入PVP戰鬥頁面")
                