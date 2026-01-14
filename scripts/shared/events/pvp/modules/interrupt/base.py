from scripts.shared.events.pvp.enum import PvPImg
from scripts.shared.controller.context import GameContext
from core.actions.vision import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from scripts.shared.utils.retry import connection_retry
from scripts.shared.constants import Battle, MainView, Leonard, Confirm
from core.base.exceptions import GameError
import time

class PvPMenuInterruptHandler:
    def __init__(self, context: GameContext):
        self.ctx = context

    def handle(self):
        cnt = 0
        start_time = time.time()    
        while time.time() - start_time < 60.0:
            if exist_click(self.ctx.serial, PvPImg.LVL_DOWN.value, wait_time=1.0):
                cnt = 0
                continue
            if exist_click(self.ctx.serial, Leonard.TP_POINT.value, wait_time=0.5):
                cnt = 0
                continue
            if exist_click(self.ctx.serial, Leonard.TP_JUMP.value, wait_time=0.5):
                cnt = 0
                continue
            if exist_click(self.ctx.serial, PvPImg.CLOSE_TIPS.value, wait_time=0.5):
                cnt = 0
                continue
            if exist(self.ctx.serial, PvPImg.SEASON_END_TEXT.value, threshold=0.9):
                cnt = 0
                wait_click(self.ctx.serial, Confirm.SMALL.value, wait_time=1.0)
                continue
            if exist(self.ctx.serial, PvPImg.TEXT.value, threshold=0.9):
                cnt += 1
                if cnt >= 2:
                    return
                else:
                    time.sleep(0.5)
        raise GameError("PvP 選單 interrupt 處理超時")