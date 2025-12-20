import time
import os
from core.system.logger import log_msg
from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, back, drag, find_spotlight_center
from core.base.exceptions import GameError
from scripts.shared.constants import MainView, Confirm, Retry
import time
from core.actions.screen import wait_click, exist_click, exist, wait, get_pos, check_region_brightness
from core.base.exceptions import GameError
from scripts.shared.events.season_pass.enum import SeasonPassImg
from scripts.shared.constants import MainView
from typing import List
from scripts.shared.controller.context import GameContext

class DimmedStrategy():
    """
    brightness is too low
    """
    def __init__(self, ctx: GameContext):
        self.ctx = ctx

    def handle_supported(self) -> bool:
        if exist(self.ctx.serial, MainView.CLOSE_PVP.value, threshold=0.9): # change to detect text for better accuracy
            wait_click(self.ctx.serial, MainView.CLOSE_PVP.value)
            return True
        
        if exist(self.ctx.serial, MainView.POLICY_TEXT.value, threshold=0.99):
            wait_click(self.ctx.serial, MainView.CLOSE_BOARD.value)
            return True
        
        if exist(self.ctx.serial, SeasonPassImg.POP_DETAIL_TEXT.value, threshold=0.99):
            wait_click(self.ctx.serial, Confirm.CANCEL.value)
            return True
       
        if exist_click(self.ctx.serial, MainView.SKIP.value, threshold=0.85):
            if wait(self.ctx.serial, MainView.SKIP_TUTORIAL_TEXT.value, threshold=0.9, timeout=3.0):
                wait_click(self.ctx.serial, Confirm.SMALL.value)
            return True

        if exist_click(self.ctx.serial, MainView.SKIP_2.value, threshold=0.9):
            return True
        
        if exist(self.ctx.serial, MainView.BOARD_END.value, threshold=0.95) and exist(self.ctx.serial, MainView.CLOSE_BOARD2.value, threshold=0.9):
            wait_click(self.ctx.serial, MainView.CLOSE_BOARD2.value)
            return True
        return False
    