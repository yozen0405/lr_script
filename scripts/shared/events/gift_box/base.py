from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from scripts.shared.utils.retry import connection_retry
from scripts.shared.constants import Settlement, Confirm, Battle, MainView, Retry, Positions
from core.base.exceptions import GameError
from core.system.logger import log_msg
from typing import Optional, Tuple
from scripts.shared.events.main_stage.enum import MainStage
from core.system.config import Config
from scripts.shared.constants import Leonard, Battle
from scripts.shared.events.pvp.enum import PvP
from scripts.shared.events.gift_box.enum import GiftBoxImg
from scripts.shared.controller.context import GameContext
import time

class GiftBoxBase:
    def __init__(self, context: GameContext):
        self.ctx = context

    def on_page(self) -> bool:
        return exist(self.ctx.serial, GiftBoxImg.TEXT.value, threshold=0.9)

    def enter_menu(self):
        if not exist(self.ctx.serial, GiftBoxImg.TEXT.value, threshold=0.9):
            if not wait_click(self.ctx.serial, GiftBoxImg.BTN.value, threshold=0.8):
                raise GameError("無法進入Gift box活動選單")
            connection_retry(self.ctx.serial, appear=GiftBoxImg.TEXT.value, timeout=40.0)
    
    def leave_menu(self):
        if not exist_click(self.ctx.serial, MainView.CLOSE_BOARD.value):
            raise GameError("無法離開Gift box活動選單")
        connection_retry(self.ctx.serial, vanish=GiftBoxImg.TEXT.value, timeout=40.0)
    
    def claim(self):
        start_time = time.time()
        
        claimed = False
        while time.time() - start_time < 300:
            if exist(self.ctx.serial, Retry.TEXT1.value, threshold=0.9):
                exist_click(self.ctx.serial, Retry.BTN.value)
                continue

            if exist(self.ctx.serial, GiftBoxImg.POP_UNCLAIMED_TEXT.value, threshold=0.9):
                wait_click(self.ctx.serial, Confirm.SMALL.value)
                continue

            if exist(self.ctx.serial, GiftBoxImg.POP_ACCEPT_TEXT.value, threshold=0.9):
                claimed = True
                wait_click(self.ctx.serial, Confirm.SMALL.value)
                continue

            if claimed:
                exist_click(self.ctx.serial, MainView.CLOSE_BOARD.value)
                if not exist(self.ctx.serial, GiftBoxImg.TEXT.value, threshold=0.9):
                    return
        raise GameError("領取禮物超時")
    
def claim_gift_box(context: GameContext):
    gift_box = GiftBoxBase(context)
    gift_box.enter_menu()
    gift_box.claim()