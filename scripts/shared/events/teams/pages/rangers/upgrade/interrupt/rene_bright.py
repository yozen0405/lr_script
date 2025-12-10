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

class ReneBrightStrategy():
    def __init__(self, serial):
        self.serial = serial
    
    def _has_rene(self) -> bool:
        pos = get_pos(self.serial, TeamsImg.UPGRADE_PAGE_RENE.value, threshold=0.8, return_center=False)
        if pos is not None and check_region_brightness(self.serial, region=pos, threshold=45):
            return True
        return False

    def proccess(self):
        if not self._has_rene():
            raise GameError("Rene not found on upgrade page.")
        start_time = time.time()
        while time.time() - start_time < 30.0:
            if exist(self.serial, TeamsImg.UPGRADE_SUCCESS.value, threshold=0.9):
                return
            
            if exist(self.serial, Retry.TEXT1.value, threshold=0.9) or exist(self.serial, Retry.TEXT2.value, threshold=0.9):
                wait_click(self.serial, Retry.BTN.value)
                continue
        
            if exist_click(self.serial, TeamsImg.UPGRADE_LVL_BTN.value, threshold=0.9):
                continue
            else:
                drag(self.serial, (80, 574), (478, 341))
                continue
        
        raise GameError("Upgrade success interrupt handling timed out.")