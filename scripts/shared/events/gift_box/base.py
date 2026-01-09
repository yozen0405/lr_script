from core.actions.vision import check_region_brightness, wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from scripts.shared.utils.retry import connection_retry
from scripts.shared.constants import Settlement, Confirm, Battle, MainView, Retry, Positions
from core.base.exceptions import GameError
from core.system.logging.logger import log_msg
from typing import Optional, Tuple
from scripts.shared.events.main_stage.enum import MainStageImg
from core.system.config import Config
from scripts.shared.constants import Leonard, Battle
from scripts.shared.events.pvp.enum import PvP
from scripts.shared.events.gift_box.enum import GiftBoxImg
from scripts.shared.controller.context import GameContext
import time

class GiftBoxBase:
    def __init__(self, context: GameContext):
        self.ctx = context
        self.lucky_bag_region = None

    def on_page(self) -> bool:
        return exist(self.ctx.serial, GiftBoxImg.TEXT.value, threshold=0.9)
    
    def on_interrupt(self) -> bool:
        loc = get_pos(self.ctx.serial, GiftBoxImg.TEXT.value, threshold=0.9, return_center=False)
        if loc is None:
            return True
        if check_region_brightness(self.ctx.serial, loc, threshold=45):
            return False
        return True

    def enter_menu(self):
        if not exist(self.ctx.serial, GiftBoxImg.TEXT.value, threshold=0.9):
            if not wait_click(self.ctx.serial, GiftBoxImg.BTN.value, threshold=0.8):
                raise GameError("無法進入Gift box活動選單")
            connection_retry(self.ctx.serial, appear=GiftBoxImg.TEXT.value, timeout=60.0)
    
    def leave_menu(self):
        log_msg(self.ctx.serial, "離開Gift box活動選單")
        if not exist_click(self.ctx.serial, MainView.CLOSE_BOARD.value):
            raise GameError("無法離開Gift box活動選單")
        connection_retry(self.ctx.serial, vanish=GiftBoxImg.TEXT.value, timeout=60.0)
    
    def claim_all(self):
        start_time = time.time()
        
        if not wait_click(self.ctx.serial, GiftBoxImg.ACCEPT_ALL.value, threshold=0.9, timeout=3.0):
            return False

        pressed = False
        cnt = 0
        while time.time() - start_time < 300:
            if exist(self.ctx.serial, Retry.TEXT1.value, threshold=0.9) or exist(self.ctx.serial, Retry.TEXT2.value, threshold=0.9):
                if not exist_click(self.ctx.serial, Retry.BTN.value):
                    exist_click(self.ctx.serial, Confirm.SMALL.value)
                continue

            if pressed:
                if not self.on_interrupt():
                    cnt += 1
                    if cnt >= 2:
                        return True
            
            if exist(self.ctx.serial, GiftBoxImg.POP_UNCLAIMED_TEXT.value, threshold=0.9):
                wait_click(self.ctx.serial, Confirm.SMALL.value, wait_time=1.0)
                pressed = True
                cnt = 0
                continue

            if exist(self.ctx.serial, GiftBoxImg.POP_CONFIRM_TEXT.value, threshold=0.9):
                wait_click(self.ctx.serial, Confirm.SMALL.value)
                cnt = 0
                continue

            if exist(self.ctx.serial, GiftBoxImg.ALL_ACCEPTED_TEXT.value, threshold=0.9):
                wait_click(self.ctx.serial, Confirm.SMALL.value)
                pressed = True
                cnt = 0
                continue
            
        raise GameError("領取禮物超時")
    
    def claim_contents(self):
        start_time = time.time()

        opened = False
        not_found_cnt = 0
        while time.time() - start_time < 50.0:
            if exist(self.ctx.serial, Retry.TEXT1.value, threshold=0.9):
                exist_click(self.ctx.serial, Retry.BTN.value)
                continue
            
            if exist_click(self.ctx.serial, Confirm.BIG1.value, threshold=0.9, wait_time=1.0):
                opened = True
                not_found_cnt = 0
                continue

            if exist_click(self.ctx.serial, GiftBoxImg.ACCEPT_BTN.value, region=self.lucky_bag_region, threshold=0.8):
                not_found_cnt = 0
                continue

            if exist_click(self.ctx.serial, Settlement.BRONZE_BOX.value, threshold=0.8, wait_time=2.0):
                opened = True
                not_found_cnt = 0
                continue
            
            if opened:
                not_found_cnt += 1
                if not_found_cnt >= 4:
                    log_msg(self.ctx.serial, "完成福袋內容領取")
                    return
        raise GameError("領取福袋內容超時")
    
    # def claim_lucky_bag(self):
    #     for _ in range(3):
    #         drag(self.ctx.serial, (521, 325), (521, 144), duration=500, wait_time=2.5)
    #         loc = get_pos(self.ctx.serial, GiftBoxImg.LUCKY_BAG.value, threshold=0.9)
    #         if loc:
    #             (x, y) = loc
    #             self.lucky_bag_region = (x - 30, y - 50, x + 407, y + 55)
    #             self.claim_contents()
    #             return
                
    
def claim_gift_box(context: GameContext):
    gift_box = GiftBoxBase(context)
    gift_box.enter_menu()
    gift_box.claim_all()
    #gift_box.claim_lucky_bag()
    gift_box.leave_menu()