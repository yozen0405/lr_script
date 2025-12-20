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

class LeonardBgHappyStrategy():
    def __init__(self, serial):
        self.serial = serial
    
    def proccess(self):
        if not exist_click(self.serial, Leonard.BG_HAPPY.value, threshold=0.8):
            raise GameError("Not in Leonard BG Happy interrupt.")
        
        start_time = time.time()
        saved = False
        while time.time() - start_time < 60.0:
            if exist(self.serial, Retry.TEXT1.value, threshold=0.9) or exist(self.serial, Retry.TEXT2.value, threshold=0.9):
                wait_click(self.serial, Retry.BTN.value)
                continue

            if saved and not exist(self.serial, TeamsImg.TEXT.value, threshold=0.9):
                return

            if exist_click(self.serial, Leonard.BG_HAPPY.value, threshold=0.8):
                if exist(self.serial, TeamsImg.ARRANGE_DIALOGUE_UP.value, threshold=0.9):
                    drag(self.serial, (182, 576), (641, 285), duration=500, wait_time=1.0)
                    continue
                elif exist(self.serial, TeamsImg.ARRANGE_DIALOGUE_DOWN.value, threshold=0.9):
                    drag(self.serial, (641, 285), (182, 576), duration=500, wait_time=1.0)
                    continue
                continue

            if exist_click(self.serial, MainView.SKIP.value):
                if wait(self.serial, MainView.SKIP_TUTORIAL_TEXT.value, threshold=0.9):
                    wait_click(self.serial, Confirm.SMALL.value)
                continue

            if exist_click(self.serial, TeamsImg.SAVE.value, threshold=0.9):
                saved = True
                continue

        raise GameError("Leonard BG Happy interrupt handling timed out.")