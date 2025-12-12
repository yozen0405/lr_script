import time
import os
from core.system.logger import log_msg
from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, back, drag
from core.base.exceptions import GameError
from scripts.shared.constants import MainView, Confirm, Retry
import time
from abc import ABC, abstractmethod
from enum import Enum, auto
from core.actions.screen import wait_click, exist_click, exist, wait
from core.base.exceptions import GameError
from scripts.shared.events.season_pass.enum import SeasonPassImg
from scripts.shared.constants import MainView
from scripts.shared.controller.context import GameContext

class NoAvatarStrategy():
    """
    cant find avatar
    """
    def __init__(self, context: GameContext):
        self.ctx = context

    def handle_supported(self) -> bool:
        if exist(self.ctx.serial, MainView.BOARD_DONT_SHOW.value, threshold=0.9):
            wait_click(self.ctx.serial, MainView.BOARD_DONT_SHOW.value)
            wait_click(self.ctx.serial, MainView.CLOSE_BOARD2.value)
            return True
        
        if exist(self.ctx.serial, MainView.BOARD_END.value, threshold=0.95) and exist(self.ctx.serial, MainView.CLOSE_BOARD2.value, threshold=0.9):
            wait_click(self.ctx.serial, MainView.CLOSE_BOARD2.value)
            return True
        
        if exist(self.ctx.serial, MainView.COMEBACK.value, threshold=0.99):
            wait_click(self.ctx.serial, MainView.CLOSE_BOARD2.value)
            return True
        
        if exist(self.ctx.serial, MainView.SPECIAL_OFFERS.value, threshold=0.99):
            wait_click(self.ctx.serial, MainView.CLOSE_BOARD2.value)
            return True
    
        if exist(self.ctx.serial, MainView.BUFF_EVENT.value, threshold=0.9):
            wait_click(self.ctx.serial, MainView.CLOSE_BOARD2.value)
            return True
        return False
    