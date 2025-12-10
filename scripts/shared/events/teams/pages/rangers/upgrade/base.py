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
from scripts.shared.events.teams.pages.rangers.upgrade.interrupt.upgrade_success import UpgradeSuccessStrategy
from scripts.shared.events.teams.pages.rangers.upgrade.interrupt.rene_bright import ReneBrightStrategy
from scripts.shared.events.teams.pages.rangers.upgrade.interrupt.rene_dark import ReneDarkStrategy
from scripts.shared.controller.enum import TaskStatus
from scripts.shared.controller.context import GameContext

import time

class RangerUpgradePage():
    def __init__(self, context: GameContext):
        self.ctx = context
        self.upgrade_success_strategy = UpgradeSuccessStrategy(context.serial)
        self.rene_bright_strategy = ReneBrightStrategy(context.serial)
        self.rene_dark_strategy = ReneDarkStrategy(context.serial)

    def on_page(self) -> bool:
        has_filter = exist(self.ctx.serial, TeamsImg.FILTER_BTN.value, threshold=0.9)
        has_sell = exist(self.ctx.serial, TeamsImg.SELL_BTN.value, threshold=0.9)
        return has_filter and not has_sell
    
    def on_interrupt(self) -> bool:
        if not self.on_page():
            return False
        
        loc = get_pos(self.ctx.serial, TeamsImg.FILTER_BTN.value, threshold=0.8, return_center=False)
        if not loc:
            if exist(self.ctx.serial, TeamsImg.UPGRADE_SUCCESS.value, threshold=0.9):
                return True

        if not check_region_brightness(self.ctx.serial, region=loc, threshold=45):
            return True
        return False

    def on_rene_upgrade(self):
        self.rene_bright_strategy.proccess()
        self.upgrade_success_strategy.proccess()
        self.rene_dark_strategy.proccess()

    def enter_menu(self):
        if not self.on_page():
            if exist_click(self.ctx.serial, TeamsImg.UPGRADE_BTN.value, threshold=0.9):
                connection_retry(self.ctx.serial, appear=(TeamsImg.TEXT.value, 0.9), timeout=40.0)
            else:
                raise GameError("Not on ranger upgrade page.")
            
    def leave_menu(self):
        if not self.on_page():
            return
        if not exist_click(self.ctx.serial, MainView.BACK.value):
            raise GameError("Cannot exit ranger upgrade page.")
        connection_retry(self.ctx.serial, appear=(TeamsImg.TEXT.value, 0.9), timeout=40.0)

    def upgrade_ranger(self):
        # 知後可能加上 filter
        
        start_time = time.time()
        fg = False
        while time.time() - start_time < 50.0:
            if exist_click(self.ctx.serial, TeamsImg.UPGRADE_SUCCESS.value, threshold=0.9):
                fg = True
                continue

            if fg and exist(self.ctx.serial, TeamsImg.FILTER_BTN.value, threshold=0.9):
                return 
            
            if exist(self.ctx.serial, Retry.TEXT1.value, threshold=0.9) or exist(self.ctx.serial, Retry.TEXT2.value, threshold=0.9):
                wait_click(self.ctx.serial, Retry.BTN.value)
                continue
            
            if exist_click(self.ctx.serial, TeamsImg.LVL_UP_POP_TEXT.value):
                wait_click(self.ctx.serial, Confirm.SMALL.value)
                continue

            if exist_click(self.ctx.serial, TeamsImg.UPGRADE_LVL_BTN.value, threshold=0.9):
                continue
            else:
                drag(self.ctx.serial, (609, 618), (609, 358)) 
                continue
        raise GameError("Ranger upgrade timed out.")