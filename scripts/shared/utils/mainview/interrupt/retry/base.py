import time
import os
from core.system.logger import log_msg
from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, back, drag
from core.base.exceptions import GameError
from scripts.shared.constants import MainView, Confirm, Retry
import time
from core.actions.screen import wait_click, exist_click, exist, wait
from core.base.exceptions import GameError
from scripts.shared.events.season_pass.enum import SeasonPassImg
from scripts.shared.constants import MainView
from scripts.shared.utils.mainview.interrupt.base import BaseStrategy

class RetryStrategy(BaseStrategy):
    def __init__(self, serial):
        self.serial = serial

    def check(self):
        if exist(self.serial, Retry.TEXT1.value, threshold=0.9):
            return True
        if exist(self.serial, Retry.TEXT2.value, threshold=0.9):
            return True
        return False

    def proccess(self):
        if exist(self.serial, Retry.TEXT1.value, threshold=0.9):
            wait_click(self.serial, Retry.BTN.value)
            return
        
        if exist(self.serial, Retry.TEXT2.value, threshold=0.9):
            wait_click(self.serial, Retry.BTN.value)
            return