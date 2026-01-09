from scripts.shared.events.season_pass.enum import SeasonPassImg, SeasonPassState
from scripts.shared.constants import Confirm, MainView, Retry, Leonard
from core.actions.vision import wait_click, exist_click, exist, wait
from scripts.shared.utils.retry import connection_retry
from core.base.exceptions import GameError
from scripts.shared.controller.context import GameContext
import time

class SeasonPassBase:
    def __init__(self, ctx: GameContext):
        self.ctx = ctx
        
    def enter_menu(self):
        if not exist(self.ctx.serial, SeasonPassImg.TEXT.value, threshold=0.9):
            if wait_click(self.ctx.serial, SeasonPassImg.ICON.value, threshold=0.97):
                connection_retry(self.ctx.serial, vanish=[(SeasonPassImg.ICON.value, 0.97)], timeout=40.0)
            else:
                raise GameError("無法進入季票活動選單")
            
        if exist(self.ctx.serial, SeasonPassImg.POP_TEXT.value, threshold=0.9):
            wait_click(self.ctx.serial, Confirm.SMALL.value)
            
        self.handle_pre_anime()

    def leave_menu(self):
        wait_click(self.ctx.serial, MainView.BACK.value)
        connection_retry(self.ctx.serial, vanish=SeasonPassImg.TEXT.value, timeout=40.0)
        
    def handle_pre_anime(self):
        if not wait(self.ctx.serial, Leonard.TP_HAPPY2.value, threshold=0.9, timeout=3.0):
            return False
        for _ in range(13):
            wait_click(self.ctx.serial, SeasonPassImg.TEXT.value)
        return True
    
    def _on_nav(self):
        start_time = time.time()
        not_found_count = 0
        while time.time() - start_time < 300:
            if exist(self.ctx.serial, Retry.TEXT1.value, threshold=0.9) or exist(self.ctx.serial, Retry.TEXT2.value, threshold=0.9):
                wait_click(self.ctx.serial, Retry.BTN.value)
                not_found_count = 0
                continue

            if exist(self.ctx.serial, SeasonPassImg.EXP_UP_TEXT.value, threshold=0.9):
                wait_click(self.ctx.serial, Confirm.BIG2.value)
                not_found_count = 0
                continue

            if exist(self.ctx.serial, SeasonPassImg.CLAIMED_TEXT.value, threshold=0.9):
                wait_click(self.ctx.serial, Confirm.SMALL.value)
                not_found_count = 0
                continue

            if exist_click(self.ctx.serial, SeasonPassImg.CLAIM.value):
                not_found_count = 0
                continue
            else:
                not_found_count += 1

            if not_found_count >= 2:
                return
        raise GameError("Failed to navigate Season Pass.")
    
    def handle_daily_nav(self):
        exist_click(self.ctx.serial, SeasonPassImg.DAILY_NAV.value, threshold=0.99)
        self._on_nav()

    def handle_weekly_nav(self):
        exist_click(self.ctx.serial, SeasonPassImg.WEELKY_NAV.value, threshold=0.99)
        self._on_nav()
    
    def handle_pass_nav(self):
        wait_click(self.ctx.serial, SeasonPassImg.PASS_NAV.value)
        if self.handle_pre_anime():
            wait_click(self.ctx.serial, SeasonPassImg.PASS_NAV.value)
        if not wait_click(self.ctx.serial, SeasonPassImg.TICKETS.value, threshold=0.99):
            return

        connection_retry(self.ctx.serial, appear=[(SeasonPassImg.CONGRATS.value, 0.9)], retry=[(SeasonPassImg.TICKETS.value, 0.9)], timeout=40.0)
        wait_click(self.ctx.serial, Confirm.BIG2.value)
        connection_retry(self.ctx.serial, appear=[(SeasonPassImg.HISTORY_TEXT.value, 0.8)], retry=[(Confirm.BIG2.value, 0.9)], timeout=40.0)
        wait_click(self.ctx.serial, MainView.CLOSE_BOARD.value)

def claim_tickets(ctx: GameContext):
    sp = SeasonPassBase(ctx)
    sp.enter_menu()
    sp.handle_daily_nav()
    sp.handle_weekly_nav()
    sp.handle_pass_nav()
    sp.leave_menu()

def claim_season_pass(ctx: GameContext):
    sp = SeasonPassBase(ctx)
    sp.enter_menu()
    sp.handle_daily_nav()
    sp.handle_weekly_nav()
    sp.leave_menu()