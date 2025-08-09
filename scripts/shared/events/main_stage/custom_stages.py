from scripts.shared.events.main_stage.base import BaseMainStage
from core.actions.actions import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from scripts.shared.utils.retry import connection_retry
import time
from core.base.exceptions import GameError
from core.system.logger import log_msg

class FirstStage(BaseMainStage):
    def _on_pre_start_page_prev(self):
        wait_click(self.serial, "meteor.png", threshold=0.5)

class SecondStage(BaseMainStage):
    def _on_settlement_page(self):
        if exist_click(self.serial, "skip.png"):
            wait_click(self.serial, "confirm_small.png", wait_time=0.5)

class ThirdStage(BaseMainStage):
    def _on_start_page(self):
        time.sleep(1.0)
        if not wait_click(self.serial, "speed_up_btn_off.png", wait_time=3.0):
            raise GameError("無法點擊x2")
        if not wait_click(self.serial, "speed_up_btn_on.png"):
            raise GameError("無法點擊x2")
        if not wait_click(self.serial, "speed_up_btn_on.png"):
            raise GameError("無法點擊x2")

class AutoStage(BaseMainStage):
    def _on_start_page(self):
        time.sleep(1.0)
        if not wait_click(self.serial, "auto_btn_on.png", wait_time=3.0):
            raise GameError("無法點擊 auto")
        if not wait_click(self.serial, "auto_btn_off.png"):
            raise GameError("無法點擊 auto")
        if not wait_click(self.serial, "auto_btn_off.png"):
            raise GameError("無法點擊 auto")

class FriendStage(BaseMainStage):
    def _on_start_page(self):
        for _ in range(3):
            wait_click(self.serial, self.FRIEND, wait_time=1.5)
        if wait_click(self.serial, "skip.png", timeout=25.0):
            wait_click(self.serial, "confirm_small.png", wait_time=1.0)
        
        wait_click(self.serial, "skip.png")

    def _on_pre_start_page_next(self):
        if wait_click(self.serial, "skip.png", timeout=5.0):
            wait_click(self.serial, "confirm_small.png", wait_time=1.0)
        wait_click(self.serial, "skip.png", timeout=5.0, wait_time=1.0)
        (x, y) = get_pos(self.serial, "james_friend_icon.png")
        wait_click(self.serial, (x, y - 50), wait_time=1.0)