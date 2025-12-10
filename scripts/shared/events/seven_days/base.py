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
from scripts.shared.events.seven_days.enum import SevenDaysImg

class SevenDays:
    def __init__(self, serial):
        self.serial = serial
        self.enter_pos = None

    def on_page(self) -> bool:
        return exist(self.serial, SevenDaysImg.TEXT.value, threshold=0.9)

    def enter_menu(self):
        if not exist(self.serial, SevenDaysImg.TEXT.value, threshold=0.9):
            if not wait_click(self.serial, SevenDaysImg.BTN.value, threshold=0.8):
                raise GameError("無法進入7日活動選單")
            connection_retry(self.serial, appear=SevenDaysImg.TEXT.value, timeout=40.0)
        self._on_pre_anime()
    
    def leave_menu(self):
        if not exist_click(self.serial, MainView.CLOSE_BOARD.value):
            raise GameError("無法離開7日活動選單")
        connection_retry(self.serial, vanish=SevenDaysImg.TEXT.value, timeout=40.0)

    def _on_pre_anime(self):
        if not exist(self.serial, Leonard.DIALOGUE_TAG.value, threshold=0.9):
            return
        wait_click(self.serial, MainView.SKIP.value)
        wait_click(self.serial, Confirm.SMALL.value)
        wait_click(self.serial, SevenDaysImg.INFO.value)
        wait_click(self.serial, MainView.CLOSE_BOARD.value, wait_time=1.0)

    def _claim_seven_day(self):
        wait_click(self.serial, SevenDaysImg.DAY_1_NAV.value, threshold=0.95)
        pos = get_pos(self.serial, SevenDaysImg.TOP_REWARD.value, threshold=0.9)
        if not pos:
            raise GameError("找不到升級文字")
        x, y = pos

        wait_click(self.serial, (x + 500, y))
        connection_retry(self.serial, appear=[(SevenDaysImg.CLAIMED_TEXT.value, 0.9)], timeout=40.0)
        wait_click(self.serial, Confirm.SMALL.value)

        wait_click(self.serial, SevenDaysImg.DAILY_REWARD.value)
        connection_retry(self.serial, appear=[(SevenDaysImg.CLAIMED_TEXT.value, 0.9)], timeout=40.0)
        wait_click(self.serial, Confirm.SMALL.value)

    def on_event(self):
        self.enter_menu()
        self.leave_menu()

    def claim_event(self):
        self.enter_menu()
        self._claim_seven_day()
        self.leave_menu()

    