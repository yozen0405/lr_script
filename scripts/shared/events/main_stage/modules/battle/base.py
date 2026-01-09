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
from scripts.shared.events.main_stage.session import StageSession
from scripts.shared.utils.hacks import apply_mode

class BattleBase:
    def __init__(self, context: GameContext, session: StageSession):
        self.ctx = context
        self.session = session

    def run(self):
        self.session.lose = False
        timeout = 900.0 if self.session.loop else 600.0
        start_time = time.time()

        retry_time = 0
        while time.time() - start_time < timeout:
            if exist(self.ctx.serial, MainStageImg.SETTLEMENT.value, threshold=0.9) or \
                exist(self.ctx.serial, Confirm.BIG1.value, threshold=0.9) or \
                exist(self.ctx.serial, Confirm.BIG2.value, threshold=0.9):
                return

            if exist(self.ctx.serial, Retry.TEXT1.value) or exist(self.ctx.serial, Retry.TEXT2.value):
                exist_click(self.ctx.serial, Retry.BTN.value)
                retry_time += 1
                if retry_time >= 20:
                    break
                continue

            if self.session.stage_num < 13 and not self.session.has_auto:
                if exist(self.ctx.serial, Settlement.LOSE_TEXT.value, threshold=0.95):
                    self.session.lose = True
                    return

                wait_click(self.ctx.serial, Positions.MEMBER1.value)
                wait_click(self.ctx.serial, Positions.MEMBER2.value)
                wait_click(self.ctx.serial, Positions.MEMBER3.value)
                wait_click(self.ctx.serial, Positions.MEMBER4.value)
            
            self.session.stage_cls.on_battle_start()

        raise GameError("戰鬥超時")