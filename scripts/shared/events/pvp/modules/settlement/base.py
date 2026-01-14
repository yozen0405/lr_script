import time
from core.system.logging.logger import log_msg
from core.actions.vision import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from core.actions.vision import get_main_stage_num
from core.base.exceptions import GameError
from scripts.shared.constants.positions import Positions
from scripts.shared.events.main_stage.custom_stages.base import MainStageCustomHookBase
from scripts.shared.utils.retry import connection_retry
from typing import Optional
from scripts.shared.constants import Settlement, Battle, Confirm, MainView, Leonard, Retry
from scripts.shared.events.main_stage.enum import MainStageImg, MainStageSettlementImg
from scripts.shared.controller.context import GameContext
from scripts.shared.events.pvp.enum import PvPImg
from scripts.shared.events.pvp.session import StageSession
from scripts.shared.utils.hacks import apply_mode

class StageSettlement:
    def __init__(self, context: GameContext, session: StageSession):
        self.ctx = context
        self.session = session
    
    def handle_win(self):
        connection_retry(self.ctx.serial, appear=PvPImg.SETTLEMENT_TEXT.value, timeout=40.0)
        self.session.loop += 1

        start_time = time.time()
        while time.time() - start_time < 120.0:
            if exist(self.ctx.serial, Retry.TEXT1.value):
                exist_click(self.ctx.serial, Retry.TEXT1.value)

            if exist(self.ctx.serial, Settlement.PUZZLE_FOUND_TEXT.value):
                exist_click(self.ctx.serial, Confirm.BIG2.value)
                continue

            if exist_click(self.ctx.serial, PvPImg.SETTLEMENT_TEXT.value):
                continue

            if exist(self.ctx.serial, PvPImg.TEXT.value, wait_time=3.0, threshold=0.9):
                wait_click(self.ctx.serial, PvPImg.LVL_UP.value, timeout=3.0, wait_time=2.0) # change
                return

        raise GameError("結算過程異常")
    
    def run(self):
        self.handle_win()