from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos, check_region_brightness
from core.actions.screen import back
from scripts.shared.utils.retry import connection_retry
from scripts.shared.constants import Settlement, Confirm, Battle, MainView, Retry, Positions
from core.base.exceptions import GameError
from core.system.logger import log_msg
from typing import List, Optional, Tuple
from scripts.shared.events.main_stage.enum import MainStage
from scripts.shared.events.teams.enum import TeamsImg
from scripts.shared.constants.leonard import Leonard
from scripts.shared.events.teams.pages.gears.main.interrupt.equip import EquipStrategy
from scripts.shared.events.teams.pages.gears.main.interrupt.upgrade import UpgradeStrategy
from scripts.shared.controller.context import GameContext
from scripts.shared.events.teams.enum import GearImg, WeaponType, EnhancePageImg, EnhancePagePos
import time

class GearsMainPage():
    def __init__(self, context: GameContext):
        self.ctx = context

        self.equip_strategy = EquipStrategy(context.serial)
        self.upgrade_strategy = UpgradeStrategy(context.serial)
    
    def on_page(self) -> bool:
        has_text = exist(self.ctx.serial, GearImg.TEXT.value, threshold=0.9)
        has_btn = exist(self.ctx.serial, GearImg.MAIN_PAGE_SWITCH_BTN.value, threshold=0.9)
        return has_text and has_btn

    def enter_menu(self):
        if not self.on_page():
            if exist_click(self.ctx.serial, GearImg.BTN.value, threshold=0.9):
                connection_retry(self.ctx.serial, appear=GearImg.TEXT.value, retry=GearImg.BTN.value, timeout=40.0)
            else:
                raise GameError("Not on teams page.")

    def leave_menu(self):
        if not self.on_page():
            return
        
        if not exist_click(self.ctx.serial, MainView.BACK.value):
            raise GameError("Cannot exit teams page.")
        connection_retry(self.ctx.serial, vanish=(GearImg.TEXT.value, 0.9), timeout=40.0)

    def handle_event(self) -> bool:
        if not self.on_page():
            raise GameError(self.ctx.serial, "Not on gears main page.")

        if self.equip_strategy.proccess():
            return True
        
        if self.upgrade_strategy.proccess():
            return True
        
        return False