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
from scripts.shared.events.main_stage.enum import MainStageImg, Stages, Treasure, MainStageSettlementImg
from scripts.shared.controller.context import GameContext
from scripts.shared.events.main_stage.session import StageSession
from scripts.shared.utils.hacks import apply_mode
from scripts.shared.events.main_stage.modules.treasure.base import TreasureBase

class StageSettlement:
    def __init__(self, context: GameContext, session: StageSession):
        self.ctx = context
        self.session = session

        self.treasure_interrupt = TreasureBase(self.ctx, self.session)

    def settlement_items(self):
        return [
            Settlement.ACQUIRED.value,
            (Confirm.BIG1.value, 0.9),
            (Confirm.BIG2.value, 0.9),
            (Confirm.MID.value, 0.9),
            Settlement.STOP.value,
            (MainStageImg.SETTLEMENT.value, 0.9),
            Settlement.ONE_REWARD.value
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
        if exist_click(self.ctx.serial, MainView.SKIP.value, threshold=0.85):
            wait_click(self.ctx.serial, Confirm.SMALL.value)
            return True
        return False
    
    def handle_interrupt(self):
        if not exist(self.ctx.serial, MainStageImg.NEXT_FEATURE.value):
            return False
        wait_click(self.ctx.serial, MainStageSettlementImg.AGAIN.value, wait_time=1.2)
        wait_click(self.ctx.serial, MainStageSettlementImg.NEXT.value, threshold=0.95)
        return True
    
    def handle_win(self):
        self.ctx.current_stage_num = self.session.stage_num
        self.session.loop += 1

        start_time = time.time()    
        cnt = 0
        while time.time() - start_time < 240.0:
            if exist(self.ctx.serial, Retry.TEXT1.value) or exist(self.ctx.serial, Retry.TEXT2.value):
                exist_click(self.ctx.serial, Retry.BTN.value)
                continue

            if self.handle_normal_items():
                cnt = 0
                continue

            if self.handle_interrupt():
                cnt = 0
                continue

            cnt += 1
            if cnt >= 2:
                return
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
        if self.session.lose:
            self.handle_lose()
        else:
            self.handle_win()