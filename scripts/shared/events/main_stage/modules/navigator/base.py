import time
from core.actions.vision import check_region_brightness
from core.system.logging.logger import log_msg
from core.actions.vision import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from core.base.exceptions import GameError
from scripts.shared.constants.positions import Positions
from scripts.shared.controller.context import GameContext
from scripts.shared.events.main_stage.modules.treasure.base import TreasureBase
from scripts.shared.events.main_stage.session import StageSession
from scripts.shared.utils.retry import connection_retry
from typing import Optional
from scripts.shared.constants import Settlement, Battle, Confirm, MainView, Leonard, Retry
from scripts.shared.events.main_stage.enum import MainStageImg, Stages, Treasure

class StageNavigator:
    def __init__(self, context: GameContext, session: StageSession):
        self.ctx = context
        self.session = session
        self.treasure_interrupt = TreasureBase(self.ctx, self.session)

    def on_page(self, strict: bool = False) -> bool:
        if strict:
            return wait(self.ctx.serial, MainStageImg.TEXT.value, threshold=0.9, timeout=3.0)
        return exist(self.ctx.serial, MainStageImg.TEXT.value, threshold=0.9)
    
    def on_interrupt(self):
        loc = get_pos(self.ctx.serial, MainStageImg.TEXT.value, threshold=0.9, return_center=False)
        if loc is None:
            return False
        if check_region_brightness(self.ctx.serial, loc, threshold=45):
            return False
        return True
    
    def handle_interrupt(self):
        start_time = time.time()    
        while time.time() - start_time < 60.0:
            if not self.on_interrupt():
                return False
            elif self.treasure_interrupt.handle_event():
                continue
            else:
                return True
        raise GameError("主要關卡 interrupt 處理超時")
    
    def handle_menu_page(self):
        if not self.on_page(strict=True): # already left
            if exist(self.ctx.serial, MainView.BACK.value):
                exist_click(self.ctx.serial, MainView.BACK.value)
                connection_retry(self.ctx.serial, appear=[(MainStageImg.TEXT.value, 0.9)], timeout=40.0)
            else:
                return True
        
        self.session.on_interrupt = self.handle_interrupt()

        if self.session.on_interrupt:
            return False

        if self.session.on_event:
            self.leave_menu()
            return True
            
        if self.session.custom_stage and self.session.loop >= self.session.max_loop:
            log_msg(self.ctx.serial, f"[MainStageTask] 關卡 {self.session.stage_num} 已達到最大挑戰次數 {self.session.max_loop}，停止挑戰。")
            self.leave_menu()
            return True
            
        return False
    
    def enter_menu(self):
        if self.on_page():
            return
        
        if wait_click(self.ctx.serial, MainStageImg.BTN.value):
            connection_retry(self.ctx.serial, vanish=[(MainStageImg.BTN.value, 0.75)], retry=[(MainStageImg.BTN.value, 0.75)], timeout=40.0)
        else:
            if wait_click(self.ctx.serial, MainView.BACK.value):
                connection_retry(self.ctx.serial, appear=[(MainStageImg.TEXT.value, 0.9)], timeout=40.0)
            else:
                raise GameError("無法進入主要關卡")
    
    def leave_menu(self):
        log_msg(self.ctx.serial, "離開主要關卡選單。")
        start_time = time.time()
        cnt = 0
        while time.time() - start_time < 60.0:
            if exist(self.ctx.serial, Retry.TEXT1.value) or exist(self.ctx.serial, Retry.TEXT2.value):
                exist_click(self.ctx.serial, Retry.BTN.value)
                continue

            if exist(self.ctx.serial, MainStageImg.PRE_START_TEXT.value, threshold=0.9):
                exist_click(self.ctx.serial, MainView.BACK.value)
                cnt = 0
                continue

            cnt += 1
            if cnt >= 2:
                return

        raise GameError("無法離開主要關卡選單")
       