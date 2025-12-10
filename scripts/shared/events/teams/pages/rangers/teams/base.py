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
from scripts.shared.events.teams.pages.rangers.teams.interrupt.leonard_bg_happy import LeonardBgHappyStrategy
from scripts.shared.events.teams.pages.rangers.teams.interrupt.other import OtherStrategy
from scripts.shared.controller.enum import TaskStatus
from scripts.shared.controller.context import GameContext
import time

class TeamsPage():
    def __init__(self, context: GameContext):
        self.ctx = context
        self.leonard_bg_happy_strategy = LeonardBgHappyStrategy(context.serial)
        self.other_strategy = OtherStrategy(context.serial)
    
    def on_page(self) -> bool:
        has_sell_btn = exist(self.ctx.serial, TeamsImg.SELL_BTN.value, threshold=0.95)
        has_text = exist(self.ctx.serial, TeamsImg.TEXT.value, threshold=0.95)
        has_switch_text = exist(self.ctx.serial, TeamsImg.SWITCH_TEXT.value, threshold=0.95)
        return has_sell_btn or has_text or has_switch_text
    
    def on_interrupt(self) -> bool:
        if not self.on_page():
            return False
        loc = get_pos(self.ctx.serial, TeamsImg.SELL_BTN.value, threshold=0.95)
        if not check_region_brightness(self.ctx.serial, region=loc, threshold=45):
            return True
        return False
    
    def on_jessica_event(self):
        self.leonard_bg_happy_strategy.proccess()

    def enter_menu(self):
        if not self.on_page():
            if exist_click(self.ctx.serial, TeamsImg.BTN.value, threshold=0.9):
                connection_retry(self.ctx.serial, vanish=TeamsImg.BTN.value, retry=TeamsImg.BTN.value, timeout=40.0)
            else:
                raise GameError("Not on teams page.")

        if self.on_interrupt():
            if not self.other_strategy.proccess():
                raise GameError("Cannot resolve interrupt in teams page.")

    def leave_menu(self):
        if not self.on_page():
            return
        
        if self.on_interrupt():
            if not self.other_strategy.proccess():
                raise GameError("Cannot resolve interrupt in teams page.")

        if not exist_click(self.ctx.serial, MainView.BACK.value):
            raise GameError("Cannot exit teams page.")
        connection_retry(self.ctx.serial, vanish=(TeamsImg.TEXT.value, 0.9), timeout=40.0)

    def select_ranger(self):
        # 這邊不嚴謹
        wait_click(self.ctx.serial, (100, 680))