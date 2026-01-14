from core.actions.vision import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos, check_region_brightness
from scripts.shared.constants import Settlement, Confirm, Battle, Retry, MainView, Leonard
from scripts.shared.constants.view import GameView
from scripts.shared.events.main_stage.enum import MainStageImg
from scripts.shared.utils.retry import connection_retry
from scripts.shared.events.pvp.enum import PvPImg
from core.base.exceptions import GameError
from core.system.logging.logger import log_msg
from scripts.shared.utils.hacks import apply_mode
from scripts.shared.controller.context import GameContext
from scripts.shared.events.pvp.session import StageSession
import time

class StagePreperation:
    def __init__(self, context: GameContext, session: StageSession):
        self.ctx = context
        self.session = session

    def leave_page(self):
        start_time = time.time()
        cnt = 0
        while time.time() - start_time < 60.0:
            if exist(self.ctx.serial, Retry.TEXT1.value, threshold=0.9) or exist(self.ctx.serial, Retry.TEXT2.value, threshold=0.9):
                wait_click(self.ctx.serial, Retry.BTN.value)
                continue

            if exist(self.ctx.serial, Battle.NO_FEATHER.value, threshold=0.9):
                wait_click(self.ctx.serial, Confirm.CANCEL_SMALL.value)
                cnt = 0 
                continue

            if exist(self.ctx.serial, Battle.NEXT.value, threshold=0.9):
                wait_click(self.ctx.serial, MainView.BACK.value, wait_time=1.0)
                cnt = 0
                continue

            if exist(self.ctx.serial, Battle.START.value, threshold=0.9):
                wait_click(self.ctx.serial, MainView.BACK.value, wait_time=1.0)
                cnt = 0
                continue

            cnt += 1
            if cnt >= 2:
                return
        raise GameError("PVP 離開頁面超時")

    def run(self):
        log_msg(self.ctx.serial, "PVP 任務開始")
        exist_click(self.ctx.serial, Battle.AUTO_BTN_OFF2.value, threshold=0.99)

        start_time = time.time()
        pressed_start = False
        pressed_next = False
        cnt = 0
        while time.time() - start_time < 120.0:
            if exist(self.ctx.serial, Retry.TEXT1.value, threshold=0.9) or exist(self.ctx.serial, Retry.TEXT2.value, threshold=0.9):
                wait_click(self.ctx.serial, Retry.BTN.value)
                continue
            
            if exist_click(self.ctx.serial, Battle.START.value, threshold=0.9, wait_time=1.0):
                pressed_start = True
                cnt = 0
            elif exist_click(self.ctx.serial, Battle.NEXT.value, threshold=0.8, wait_time=1.0):
                pressed_next = True
                cnt = 0

            if pressed_next:
                if exist_click(self.ctx.serial, Leonard.TP_JUMP.value, wait_time=1.0):
                    cnt = 0
            
            if pressed_start:
                cnt += 1
                if cnt >= 2:
                    return
                if exist(self.ctx.serial, Battle.NO_FEATHER.value):
                    self.leave_page()
                    self.session.end = True
                    return
                if exist(self.ctx.serial, Battle.PAUSE.value):
                    return
        raise GameError("PVP 準備階段超時")
            