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
from .enum import TutorialState

class TutorialStrategy(BaseStrategy):
    def __init__(self, serial):
        self.serial = serial

    def check(self) -> bool:
        return self._detect_state() != TutorialState.UNKNOWN

    def _detect_state(self) -> TutorialState:
        if exist(self.serial, MainView.SKIP.value, threshold=0.85):
            return TutorialState.SKIP_DIALOG
         
        if exist(self.serial, MainView.SKIP_TUTORIAL_TEXT.value, threshold=0.9):
            return TutorialState.SKIP_TUTORIAL_TEXT

        if exist(self.serial, MainView.SKIP_2.value, threshold=0.9):
            return TutorialState.GUIDE_SKIP
        
        return TutorialState.UNKNOWN
    
    def proccess(self):
        state = self._detect_state()

        if state == TutorialState.SKIP_DIALOG:
            wait_click(self.serial, MainView.SKIP.value, wait_time=1.0)
            return
        
        if state == TutorialState.SKIP_TUTORIAL_TEXT:
            wait_click(self.serial, Confirm.SMALL.value)
            return
        
        if state == TutorialState.GUIDE_SKIP:
            wait_click(self.serial, MainView.SKIP_2.value, threshold=0.85)
            return