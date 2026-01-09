from core.actions.vision import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from core.actions.vision import back
from scripts.shared.utils.retry import connection_retry
from scripts.shared.constants import Settlement, Confirm, Battle, MainView, Retry, Positions
from core.base.exceptions import GameError
from core.system.logging.logger import log_msg
from typing import Optional, Tuple
from scripts.shared.events.main_stage.enum import MainStageImg
from scripts.shared.events.wheel.enum import WheelImg

class WheelBase:
    def __init__(self, serial):
        self.serial = serial

    def enter_menu(self):
        if exist(self.serial, WheelImg.TEXT.value):
            return
        
        for _ in range(5):
            if wait_click(self.serial, WheelImg.BTN.value):
                connection_retry(self.serial, vanish=WheelImg.BTN.value, timeout=40.0)
                self._on_pre_anime()
                return
            elif exist(self.serial, MainStageImg.BTN.value):
                drag(self.serial, (800, 400), (200, 400))

        raise GameError("無法進入賓果活動")
    
    def _on_pre_anime(self):
        pass

    def _claim_mission(self):
        if not exist_click(self.serial, WheelImg.MISSION_ON.value, threshold=0.999):
            return

        connection_retry(self.serial, appear=WheelImg.MISSION_TEXT.value, timeout=40.0)
        while True:
            if exist(self.serial, WheelImg.MISSION_CLAIMED_TEXT.value, threshold=0.9):
                exist_click(self.serial, Confirm.SMALL.value)
            elif exist(self.serial, Retry.TEXT1.value):
                exist_click(self.serial, Confirm.SMALL.value)
            elif wait_click(self.serial, WheelImg.GET.value, timeout=3.0):
                continue
            else:
                wait_click(self.serial, MainView.CLOSE_BOARD.value, threshold=0.9, timeout=3.0)
                if not wait_vanish(self.serial, MainView.CLOSE_BOARD.value, threshold=0.9, timeout=3.0):
                    continue
                else:
                    break
        
    def run(self):
        log_msg(self.serial,"轉盤活動開始")
        self.enter_menu()
        self._claim_mission()
        log_msg(self.serial, "轉盤活動結束")

def wheel_attempt(serial):
    wheel = WheelBase(serial)
    wheel.run()