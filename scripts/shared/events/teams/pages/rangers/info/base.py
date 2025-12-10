from core.actions.image_utils import find_spotlight_center
from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos, check_region_brightness
from core.actions.screen import back
from scripts.shared.events.teams.enum import GearImg
from scripts.shared.utils.retry import connection_retry
from scripts.shared.constants import Settlement, Confirm, Battle, MainView, Retry, Positions
from core.base.exceptions import GameError
from core.system.logger import log_msg
from typing import Optional, Tuple
from scripts.shared.events.main_stage.enum import MainStage
from scripts.shared.events.teams.enum import TeamsImg
from scripts.shared.constants.leonard import Leonard
from scripts.shared.controller.enum import TaskStatus
from scripts.shared.controller.context import GameContext
import time

class RangerInfoPage():
    def __init__(self, context: GameContext):
        self.ctx = context

        self.GEAR_REGION = (208, 455, 542, 533)
        self.UPGRADE_REGION = (265, 533, 491, 638)
    
    def on_page(self) -> bool:
        loc = self._get_loc()
        return loc is not None
    
    def on_interrupt(self) -> bool:
        loc = self._get_loc()
        if not check_region_brightness(self.ctx.serial, region=loc, threshold=45):
            return True
        return False
    
    def _on_talent_anime(self):
        if not exist_click(self.ctx.serial, Leonard.TP_CLAP2.value, threshold=0.95):
            return False

        start_time = time.time()
        cnt = 0
        while time.time() - start_time < 30.0:
            if exist_click(self.ctx.serial, Leonard.TP_CLAP2.value, threshold=0.95):
                cnt = 0
                continue
            
            if exist_click(self.ctx.serial, Leonard.TP_STICK.value, threshold=0.95):
                cnt = 0
                continue
            
            if exist_click(self.ctx.serial, Leonard.TP_POINT3.value, threshold=0.95):
                cnt = 0
                continue

            if exist_click(self.ctx.serial, Leonard.TP_THUMBS_UP.value, threshold=0.95):
                cnt = 0
                continue

            if exist_click(self.ctx.serial, Leonard.TP_HAPPY2.value, threshold=0.95):
                cnt = 0
                continue

            cnt += 1
            if cnt >= 2:
                return True
        raise GameError("Talent animation handling timed out.")

    def _on_rene_event(self):
        if not self.on_page():
            raise GameError("Not on ranger info page.")

        start_time = time.time()
        while time.time() - start_time < 40.0:
            if exist(self.ctx.serial, Retry.TEXT1.value, threshold=0.9) or exist(self.ctx.serial, Retry.TEXT2.value, threshold=0.9):
                wait_click(self.ctx.serial, Retry.BTN.value)
                continue

            if exist_click(self.ctx.serial, MainView.SKIP.value):
                if exist(self.ctx.serial, MainView.SKIP_TUTORIAL_TEXT.value):
                    wait_click(self.ctx.serial, Confirm.SMALL.value)
                continue
            
            if not self.on_page():
                return

            pos = find_spotlight_center(self.ctx.serial)
            if pos and Positions.is_in_region(pos, self.GEAR_REGION):
                exist_click(self.ctx.serial, GearImg.BTN.value)
                continue

            if pos and Positions.is_in_region(pos, self.UPGRADE_REGION):
                exist_click(self.ctx.serial, TeamsImg.UPGRADE_BTN.value)
                continue
        raise GameError("Early tutorial handling timed out.")
    
    def enter_menu(self):
        if not self.on_page():
            raise GameError("Not on ranger info page.")

        if self.on_interrupt():
            if self._on_talent_anime():
                return
            raise GameError("Ranger info page interrupted.")
        
    def leave_menu(self):
        if not self.on_page():
            return
        if not exist_click(self.ctx.serial, MainView.CLOSE_BOARD2.value, threshold=0.9):
            raise GameError("Cannot exit ranger upgrade page.")
    
    def go_gear_page(self):
        self.enter_menu()
        
        start_time = time.time()
        while time.time() - start_time < 30.0:
            if exist(self.ctx.serial, GearImg.TEXT.value, threshold=0.9):
                return
            if exist(self.ctx.serial, Retry.TEXT1.value, threshold=0.9) or exist(self.ctx.serial, Retry.TEXT2.value, threshold=0.9):
                wait_click(self.ctx.serial, Retry.BTN.value)
                continue

            if exist_click(self.ctx.serial, TeamsImg.SAVE.value, threshold=0.9):  
                continue

            if exist_click(self.ctx.serial, GearImg.BTN.value, threshold=0.9):
                continue
        raise GameError("Cannot enter gear page.")

    def go_upgrade_page(self):
        self.enter_menu()

        start_time = time.time()
        while time.time() - start_time < 30.0:
            if exist(self.ctx.serial, TeamsImg.LVL_UP_PAGE_TEXT.value, threshold=0.9):
                return
            
            if exist(self.ctx.serial, Retry.TEXT1.value, threshold=0.9) or exist(self.ctx.serial, Retry.TEXT2.value, threshold=0.9):
                wait_click(self.ctx.serial, Retry.BTN.value)
                continue

            if exist_click(self.ctx.serial, TeamsImg.SAVE.value, threshold=0.9):  
                continue

            if exist_click(self.ctx.serial, TeamsImg.UPGRADE_BTN.value, threshold=0.9):
                continue
        raise GameError("Cannot enter ranger upgrade page.")

    def _get_loc(self) -> Optional[Tuple[int, int]]:
        loc = get_pos(self.ctx.serial, TeamsImg.POP_UP_BASIC_NAV_LIGHT.value, threshold=0.95)
        if loc:
            return loc
        loc = get_pos(self.ctx.serial, TeamsImg.POP_UP_BASIC_NAV_DARK.value, threshold=0.95)
        if loc:
            return loc
        return None

