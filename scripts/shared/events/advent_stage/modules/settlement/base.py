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
from scripts.shared.events.advent_stage.session import AdventStageSession
from scripts.shared.utils.hacks import apply_mode

class StageSettlement:
    def __init__(self, context: GameContext, session: AdventStageSession):
        self.ctx = context
        self.session = session

    def settlement_items(self):
        return [
            (Confirm.BIG1.value, 0.9),
            (Confirm.BIG2.value, 0.9),
            Settlement.ONE_REWARD.value, 
            Settlement.STOP.value, 
            (Settlement.TEXT.value, 0.9),
            Settlement.SILVER_BOX.value, 
            Settlement.BRONZE_BOX.value
        ]
    
    def handle_normal_items(self):
        for item in self.settlement_items():
            if isinstance(item, tuple):
                img, threshold = item
                if exist_click(self.ctx.serial, img, threshold=threshold, wait_time=1.0):
                    return True
            else:
                if exist_click(self.ctx.serial, item, wait_time=1.0):
                    return True
        return False
    
    def handle_win(self):
        start_time = time.time()    
        cnt = 0
        while time.time() - start_time < 240.0:
            if exist(self.ctx.serial, Retry.TEXT1.value) or exist(self.ctx.serial, Retry.TEXT2.value):
                exist_click(self.ctx.serial, Retry.BTN.value)
                continue

            if exist(self.ctx.serial, Confirm.MID.value, threshold=0.95):
                if exist(self.ctx.serial, Settlement.LOSE_TEXT.value, threshold=0.8):
                    wait_click(self.ctx.serial, Confirm.MID.value, threshold=0.95, wait_time=1.0)
                    return False
            else:
                wait_click(self.ctx.serial, Confirm.MID.value, threshold=0.95, wait_time=1.0)
                cnt = 0
                continue
                
            if self.handle_normal_items():
                cnt = 0
                continue

            cnt += 1
            if cnt >= 2:
                return True
        raise GameError("結算超時")
    
    def handle_lose(self):
        start_time = time.time()    
        cnt = 0
        while time.time() - start_time < 120.0:
            if exist(self.ctx.serial, Retry.TEXT1.value) or exist(self.ctx.serial, Retry.TEXT2.value):
                exist_click(self.ctx.serial, Retry.BTN.value)
                continue

            if exist(self.ctx.serial, Settlement.LOSE_TEXT.value, threshold=0.9):
                wait_click(self.ctx.serial, Confirm.MID.value, threshold=0.95)
                cnt = 0
                continue

            cnt += 1
            if cnt >= 2:
                return
        raise GameError("結算超時")
    
    def run(self):
        if self.handle_win() is False:
            self.handle_lose()
            self.session.lose = True
        else:
            self.session.lose = False