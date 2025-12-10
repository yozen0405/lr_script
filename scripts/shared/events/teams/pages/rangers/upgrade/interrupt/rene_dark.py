from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos, check_region_brightness
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

class ReneDarkStrategy():
    def __init__(self, serial):
        self.serial = serial
    
    def _has_rene(self) -> bool:
        pos = get_pos(self.serial, TeamsImg.UPGRADE_PAGE_RENE.value, threshold=0.8, return_center=False)
        if pos is not None and not check_region_brightness(self.serial, region=pos, threshold=45):
            return True
        return False

    def proccess(self):
        if not self._has_rene():
            raise GameError("Rene not found on upgrade page.")
        
        start_time = time.time()
        while time.time() - start_time < 30.0:
            if not exist(self.serial, TeamsImg.LVL_UP_PAGE_TEXT.value, threshold=0.9):
                return
            
            if exist(self.serial, Retry.TEXT1.value, threshold=0.9) or exist(self.serial, Retry.TEXT2.value, threshold=0.9):
                wait_click(self.serial, Retry.BTN.value)
                continue
        
            if exist_click(self.serial, MainView.SKIP.value):
                continue
            elif exist(self.serial, MainView.SKIP_TUTORIAL_TEXT.value, threshold=0.9):
                wait_click(self.serial, Confirm.SMALL.value)
                continue
            elif exist_click(self.serial, MainView.BACK.value):
                continue
                
        
        raise GameError("Upgrade success interrupt handling timed out.")