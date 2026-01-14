import time
from core.actions.vision import check_region_brightness
from core.system.logging.logger import log_msg
from core.actions.vision import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from core.base.exceptions import GameError
from scripts.shared.constants.positions import Positions
from scripts.shared.controller.context import GameContext
from scripts.shared.events.pvp.session import StageSession
from scripts.shared.utils.retry import connection_retry
from typing import Optional
from scripts.shared.constants import Settlement, Battle, Confirm, MainView, Leonard, Retry
from scripts.shared.events.pvp.enum import PvPImg
from scripts.shared.events.pvp.modules.interrupt.base import PvPMenuInterruptHandler
from scripts.shared.events.pvp.modules.navigator.utils import StageNavigatorUtils   

class StageNavigator:
    def __init__(self, context: GameContext, session: StageSession):
        self.ctx = context
        self.session = session
        self.menu_interrupt = PvPMenuInterruptHandler(self.ctx)
        self.utils = StageNavigatorUtils(self.ctx)

    def on_page(self, strict: bool = False) -> bool:
        if strict:
            return wait(self.ctx.serial, PvPImg.TEXT.value, threshold=0.9, timeout=3.0)
        return exist(self.ctx.serial, PvPImg.TEXT.value, threshold=0.9)
    
    def on_interrupt(self):
        loc = get_pos(self.ctx.serial, PvPImg.TEXT.value, threshold=0.9, return_center=False)
        if loc is None:
            return True
        if check_region_brightness(self.ctx.serial, loc, threshold=45):
            return False
        return True
    
    def handle_interrupt(self):
        if self.on_interrupt():
            self.menu_interrupt.handle()
            
    def handle_menu_page(self):
        self.handle_interrupt()

        if self.session.end:
            self.leave_menu()
            return True
        
        if self.session.loop >= self.session.max_loop:
            self.leave_menu()
            return True
            
        return False
    
    def enter_menu(self):
        self.utils._attempt_enter()
    
    def leave_menu(self):
        wait_click(self.ctx.serial, MainView.BACK.value)
        connection_retry(self.ctx.serial, vanish=[(PvPImg.TEXT.value, 0.9)], retry=MainView.BACK.value, timeout=40.0)
       