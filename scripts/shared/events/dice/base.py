from core.actions.vision import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from core.actions.vision import back
from scripts.shared.utils.retry import connection_retry
from scripts.shared.constants import Settlement, Confirm, Battle, MainView, Retry, Positions
from core.base.exceptions import GameError
from core.system.logging.logger import log_msg
from typing import Optional, Tuple
from scripts.shared.events.main_stage.enum import MainStageImg
from scripts.shared.events.dice.enum import DiceImg

class DiceBase:
    def __init__(self, serial):
        self.serial = serial

    def enter_menu(self):
        if exist(self.serial, DiceImg.TEXT.value):
            return
        
        if wait_click(self.serial, DiceImg.BTN.value, threshold=0.99):
            connection_retry(self.serial, vanish=[(DiceImg.BTN.value, 0.99)], retry=DiceImg.BTN.value, timeout=40.0)
            self._on_pre_anime()
        else:
            raise GameError("無法進入骰子活動")
    
    def _on_pre_anime(self):
        pass

    def _claim_mission(self):
        if not exist_click(self.serial, DiceImg.MISSION_ON.value, threshold=0.999):
            return
        
        connection_retry(self.serial, appear=DiceImg.MISSION_TEXT.value, timeout=40.0)
        while True:
            if exist(self.serial, DiceImg.MISSION_CLAIMED_TEXT.value, threshold=0.9):
                exist_click(self.serial, Confirm.SMALL.value)
            elif exist(self.serial, Retry.TEXT1.value):
                exist_click(self.serial, Confirm.SMALL.value)
            elif wait_click(self.serial, DiceImg.GET.value, timeout=3.0):
                continue
            else:
                wait_click(self.serial, MainView.CLOSE_BOARD.value, threshold=0.9, timeout=3.0)
                if not wait_vanish(self.serial, MainView.CLOSE_BOARD.value, threshold=0.9, timeout=3.0):
                    continue
                else:
                    break
        
    def run(self):
        log_msg(self.serial,"骰子活動開始")
        self.enter_menu()
        self._claim_mission()
        log_msg(self.serial, "骰子活動結束")

def dice_attempt(serial):
    dice = DiceBase(serial)
    dice.run()
