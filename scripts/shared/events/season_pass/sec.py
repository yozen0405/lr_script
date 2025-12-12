from scripts.shared.events.season_pass.enum import SeasonPassImg, SeasonPassState
from scripts.shared.constants import Confirm, MainView, Retry, Leonard
from core.actions.screen import wait_click, exist_click, exist, wait
from scripts.shared.utils.retry import connection_retry
from core.base.exceptions import GameError
import time

class SeasonPassBase:
    def __init__(self, serial):
        self.serial = serial
        
    def enter_menu(self):
        if not exist(self.serial, SeasonPassImg.TEXT.value, threshold=0.9):
            if wait_click(self.serial, SeasonPassImg.ICON.value, threshold=0.8):
                connection_retry(self.serial, vanish=SeasonPassImg.ICON.value, timeout=40.0)
            
            if exist(self.serial, SeasonPassImg.POP_TEXT.value, threshold=0.9):
                wait_click(self.serial, Confirm.SMALL.value)
            else:
                raise GameError("無法進入季票選單")
            
        self.handle_pre_anime()
        
    def handle_pre_anime(self):
        if not exist(self.serial, Leonard.TP_POINT2.value, threshold=0.9):
            return
        for _ in range(13):
            wait_click(self.serial, SeasonPassImg.TEXT.value)
    
    def _on_nav(self):
        start_time = time.time()
        not_found_count = 0
        while time.time() - start_time < 300:
            if exist(self.serial, Retry.TEXT1.value, threshold=0.9) or exist(self.serial, Retry.TEXT2.value, threshold=0.9):
                wait_click(self.serial, Retry.BTN.value)
                not_found_count = 0
                continue

            if exist(self.serial, SeasonPassImg.EXP_UP_TEXT.value, threshold=0.9):
                wait_click(self.serial, Confirm.BIG2.value)
                not_found_count = 0
                continue

            if exist(self.serial, SeasonPassImg.CLAIMED_TEXT.value, threshold=0.9):
                wait_click(self.serial, Confirm.SMALL.value)
                not_found_count = 0
                continue

            if exist_click(self.serial, SeasonPassImg.CLAIM.value):
                not_found_count = 0
                continue
            else:
                not_found_count += 1

            if not_found_count >= 2:
                break
        raise GameError("Failed to navigate Season Pass.")
    
    def handle_pass_nav(self):
        wait_click(self.serial, SeasonPassImg.PASS_NAV.value)
        if not exist_click(self.serial, SeasonPassImg.TICKETS.value, threshold=0.99):
            return

        connection_retry(self.serial, appear=[(SeasonPassImg.CONGRATS.value, 0.9)], timeout=40.0)
        wait_click(self.serial, Confirm.BIG2.value)
        if exist(self.serial, SeasonPassImg.HISTORY_TEXT.value, threshold=0.9):
            wait_click(self.serial, MainView.CLOSE_BOARD2.value, threshold=0.9)


class SeasonPassStandard(SeasonPassBase):
    def is_on_exit(self) -> SeasonPassState:
        return SeasonPassState.WEEKLY_DONE
    
class SeasonPassNewAcc(SeasonPassBase):
    def is_on_exit(self) -> SeasonPassState:
        return SeasonPassState.PASS_DONE

def claim_season_pass(serial):
    cls = SeasonPassStandard(serial)
    cls.run()