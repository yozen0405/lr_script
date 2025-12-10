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
from scripts.shared.utils.mainview.interrupt.base import BaseStrategy
from .enum import NoAvatarState

class NoAvatarStrategy(BaseStrategy):
    """
    cant find avatar
    """
    def __init__(self, serial):
        self.serial = serial

    def check(self) -> bool:
        return self._detect_state() != NoAvatarState.UNKNOWN

    def _detect_state(self) -> NoAvatarState:
        if exist(self.serial, MainView.BOARD_DONT_SHOW.value, threshold=0.9):
            return NoAvatarState.BOARD_DONT_SHOW
        
        if exist(self.serial, MainView.BOARD_END.value, threshold=0.95) and exist(self.serial, MainView.CLOSE_BOARD2.value, threshold=0.9):
            return NoAvatarState.BOARD_END
        
        if exist(self.serial, MainView.COMEBACK.value, threshold=0.99):
            return NoAvatarState.COMEBACK
        
        if exist(self.serial, MainView.SPECIAL_OFFERS.value, threshold=0.99):
            return NoAvatarState.SPECIAL_OFFERS
    
        if exist(self.serial, MainView.BUFF_EVENT.value, threshold=0.9):
            return NoAvatarState.BUFF_EVENT
        
        return NoAvatarState.UNKNOWN
    
    def proccess(self):
        state = self._detect_state()

        if state == NoAvatarState.BOARD_DONT_SHOW:
            wait_click(self.serial, MainView.BOARD_DONT_SHOW.value)
            wait_click(self.serial, MainView.CLOSE_BOARD2.value)
            return
        
        if state in [NoAvatarState.BOARD_END, NoAvatarState.COMEBACK, 
                     NoAvatarState.SPECIAL_OFFERS, NoAvatarState.BUFF_EVENT]:
            wait_click(self.serial, MainView.CLOSE_BOARD2.value)
            return
