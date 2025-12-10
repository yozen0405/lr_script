from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from core.actions.screen import back
from scripts.shared.utils.retry import connection_retry
from scripts.shared.constants import Settlement, Confirm, Battle, MainView, Retry, Positions
from core.base.exceptions import GameError
from core.system.logger import log_msg
from typing import Optional, Tuple
from scripts.shared.events.main_stage.enum import MainStage
from scripts.shared.events.teams.enum import TeamsImg
from scripts.shared.constants.leonard import Leonard
import time

class OtherStrategy():
    def __init__(self, serial):
        self.serial = serial

    def proccess(self) -> bool:
        start_time = time.time()
        cnt = 0
        fg = False
        while time.time() - start_time < 15.0:
            if exist_click(self.serial, TeamsImg.SAVE.value, threshold=0.85):
                cnt = 0
                fg = True
                continue

            if exist_click(self.serial, Leonard.TP_POINT2.value, threshold=0.85):
                cnt = 0
                fg = True
                continue
            
            if exist_click(self.serial, Leonard.TP_THUMBS_UP.value):
                cnt = 0
                fg = True
                continue
            
            if exist_click(self.serial, TeamsImg.SELECTOR_FINGER.value, threshold=0.85):
                wait_click(self.serial, (1035, 88))
                cnt = 0
                fg = True
                continue
            
            if exist_click(self.serial, MainView.SKIP.value, threshold=0.85):
                if exist_click(self.serial, MainView.SKIP_TUTORIAL_TEXT.value, threshold=0.95):
                    exist_click(self.serial, Confirm.SMALL.value)
                cnt = 0
                fg = True
                continue
            
            cnt += 1
            if cnt >= 2:
                return fg
        raise GameError("Other interrupt handling timed out.")