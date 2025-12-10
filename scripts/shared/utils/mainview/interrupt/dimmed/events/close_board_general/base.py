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
from .enum import CloseBoardGeneralState

class CloseBoardGeneralStrategy(BaseStrategy):
    def __init__(self, serial):
        self.serial = serial

    def check(self) -> bool:
        return self._detect_state() != CloseBoardGeneralState.UNKNOWN

    def _detect_state(self) -> CloseBoardGeneralState:
        if exist(self.serial, MainView.CLOSE_PVP.value, threshold=0.9): # change to detect text for better accuracy
            return CloseBoardGeneralState.CLOSE_PVP
        
        if exist(self.serial, MainView.POLICY_TEXT.value, threshold=0.99):
            return CloseBoardGeneralState.POLICY_TEXT
        
        if exist(self.serial, SeasonPassImg.POP_DETAIL_TEXT.value, threshold=0.99):
            return CloseBoardGeneralState.SEASON_PASS_DETAIL
        
        return CloseBoardGeneralState.UNKNOWN
    
    def proccess(self):
        state = self._detect_state()

        if state == CloseBoardGeneralState.CLOSE_PVP:
            wait_click(self.serial, MainView.CLOSE_PVP.value)
            return
        
        if state == CloseBoardGeneralState.SEASON_PASS_DETAIL:
            wait_click(self.serial, Confirm.CANCEL.value)
            return
        
        if state == CloseBoardGeneralState.POLICY_TEXT:
            wait_click(self.serial, MainView.CLOSE_BOARD2.value)
            return