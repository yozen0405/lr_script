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

class UpgradeSuccessStrategy():
    def __init__(self, serial):
        self.serial = serial
    
    def proccess(self):
        start_time = time.time()
        fg = False
        while time.time() - start_time < 30.0:
            if exist_click(self.serial, TeamsImg.UPGRADE_SUCCESS.value, threshold=0.9):
                fg = True
                continue
            else:
                return fg
        raise GameError("Upgrade success interrupt handling timed out.")