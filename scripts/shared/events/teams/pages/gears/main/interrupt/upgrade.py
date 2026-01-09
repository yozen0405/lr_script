from core.actions.vision import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from core.actions.vision import back
from scripts.shared.utils.retry import connection_retry
from scripts.shared.constants import Settlement, Confirm, Battle, MainView, Retry, Positions
from core.base.exceptions import GameError
from core.system.logging.logger import log_msg
from typing import Optional, Tuple
from scripts.shared.events.teams.enum import TeamsImg
from scripts.shared.constants.leonard import Leonard
from scripts.shared.events.teams.enum import GearImg, ArmorType, EnhancePageImg
import time

class UpgradeStrategy():
    def __init__(self, serial):
        self.serial = serial
    
    def go_upgrade_page(self):
        start_time = time.time()
        while time.time() - start_time < 30.0:
            if exist(self.serial, Retry.TEXT1.value, threshold=0.9) or exist(self.serial, Retry.TEXT2.value, threshold=0.9):
                wait_click(self.serial, Retry.BTN.value)
                continue

            if exist(self.serial, EnhancePageImg.TEXT.value, threshold=0.9):
                return

            if exist_click(self.serial, EnhancePageImg.BTN.value, threshold=0.8):
                continue

            if exist_click(self.serial, ArmorType.SHIELD.value, threshold=0.8):
                continue
        raise GameError("Go upgrade shield page interrupt handling timed out.")
    
    def upgrade_shield(self):
        start_time = time.time()

        succ = False
        while time.time() - start_time < 30.0:
            if exist(self.serial, Retry.TEXT1.value, threshold=0.9) or exist(self.serial, Retry.TEXT2.value, threshold=0.9):
                wait_click(self.serial, Retry.BTN.value)
                continue

            if exist(self.serial, EnhancePageImg.SUCCESS_TEXT.value, threshold=0.9):
                succ = True
                continue

            if exist(self.serial, MainView.SKIP.value, threshold=0.9):
                wait_click(self.serial, Confirm.SMALL.value, timeout=3.0)
                continue

            if exist_click(self.serial, EnhancePageImg.ENHANCE.value, threshold=0.9):
                continue

            if succ == False and exist_click(self.serial, ArmorType.SHIELD.value):
                continue
            
            if succ:
                if exist(self.serial, EnhancePageImg.TEXT.value, threshold=0.9):
                    wait_click(self.serial, MainView.BACK.value)
                else:
                    return
        raise GameError("Upgrade shield interrupt handling timed out.")

    def proccess(self) -> bool:
        if not exist(self.serial, ArmorType.SHIELD.value, threshold=0.8):
            return False
        
        self.go_upgrade_page()
        self.upgrade_shield()
        return True