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
from scripts.shared.events.teams.enum import GearImg, ArmorType
import time

class EquipStrategy():
    def __init__(self, serial):
        self.serial = serial
    
    def proccess(self) -> bool:
        if not wait_click(self.serial, Leonard.BG_POINT.value, threshold=0.8, timeout=7.0):
            return False
        
        start_time = time.time()
        fg = False
        while time.time() - start_time < 30.0:
            if exist(self.serial, Retry.TEXT1.value, threshold=0.9) or exist(self.serial, Retry.TEXT2.value, threshold=0.9):
                wait_click(self.serial, Retry.BTN.value)
                continue

            if exist_click(self.serial, Leonard.BG_HAPPY.value, threshold=0.8):
                continue

            if exist_click(self.serial, Leonard.BG_POINT.value, threshold=0.8):
                continue

            if exist_click(self.serial, GearImg.EQUIP_BTN.value, threshold=0.9):
                fg = True
                continue

            if fg == True:
                if exist_click(self.serial, MainView.BACK.value):
                    continue
                if not exist(self.serial, GearImg.TEXT.value, threshold=0.9):
                    return True

            if fg == False and exist_click(self.serial, ArmorType.SHIRT.value, threshold=0.95):
                continue

        raise GameError("Leonard BG Happy interrupt handling timed out.")