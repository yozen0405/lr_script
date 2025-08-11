from scripts.shared.events.main_stage.base import BaseMainStage
from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from scripts.shared.utils.retry import connection_retry
import time
from core.base.exceptions import GameError
from core.system.logger import log_msg
from scripts.shared.constants import GameView, MainView, Battle, Confirm
from scripts.shared.events.main_stage.enum import MainStage

class FirstStage(BaseMainStage):
    def _on_pre_start_page_prev(self):
        wait_click(self.serial, MainStage.METEOR, threshold=0.5)

class SecondStage(BaseMainStage):
    def _on_settlement_page(self):
        if exist_click(self.serial, MainView.SKIP):
            wait_click(self.serial, Confirm.SMALL, wait_time=0.5)

class ThirdStage(BaseMainStage):
    def _on_start_page(self):
        time.sleep(1.0)
        if not wait_click(self.serial, Battle.SPEED_BTN_OFF, wait_time=3.0):
            raise GameError("無法點擊x2")
        if not wait_click(self.serial, Battle.SPEED_BTN_ON):
            raise GameError("無法點擊x2")
        if not wait_click(self.serial, Battle.SPEED_BTN_ON):
            raise GameError("無法點擊x2")

class AutoStage(BaseMainStage):
    def _on_start_page(self):
        time.sleep(1.0)
        if not wait_click(self.serial, Battle.AUTO_BTN_ON, wait_time=3.0):
            raise GameError("無法點擊 auto")
        if not wait_click(self.serial, Battle.AUTO_BTN_OFF):
            raise GameError("無法點擊 auto")
        if not wait_click(self.serial,  Battle.AUTO_BTN_OFF):
            raise GameError("無法點擊 auto")

class FriendStage(BaseMainStage):
    def _on_start_page(self):
        for _ in range(3):
            wait_click(self.serial, self.FRIEND, wait_time=1.5)
        if wait_click(self.serial, MainView.SKIP, timeout=25.0):
            wait_click(self.serial, Confirm.SMALL, wait_time=1.0)
        
        wait_click(self.serial, MainView.SKIP)

    def _on_pre_start_page_next(self):
        if wait_click(self.serial, MainView.SKIP, timeout=5.0):
            wait_click(self.serial, Confirm.SMALL, wait_time=1.0)
        wait_click(self.serial, MainView.SKIP, timeout=5.0, wait_time=1.0)
        (x, y) = get_pos(self.serial, MainStage.JAMES_FRIEND)
        wait_click(self.serial, (x, y - 50), wait_time=1.0)