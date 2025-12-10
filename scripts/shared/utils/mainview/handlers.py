import time
import os
from core.system.logger import log_msg
from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, back, drag
from core.base.exceptions import GameError
from scripts.shared.constants import MainView, Confirm, Retry
from scripts.shared.utils.mainview.enum import MainViewState
import time
from abc import ABC, abstractmethod
from enum import Enum, auto
from core.actions.screen import wait_click, exist_click, exist, wait
from core.base.exceptions import GameError
from scripts.shared.constants import MainView
from scripts.shared.events.special_stage.selector import special_stage_enter_menu
from scripts.shared.utils.retry import connection_retry

class BaseStateHandler(ABC):
    def __init__(self, serial):
        self.serial = serial

    @abstractmethod
    def handle(self):
        """執行該狀態下的對應動作"""
        pass

class TutorialHandler(BaseStateHandler):
    def handle(self):
        wait_click(self.serial, MainView.SKIP.value, wait_time=1.0)

class SkipGuideHandler(BaseStateHandler):
    def handle(self):
        wait_click(self.serial, MainView.SKIP_2.value, threshold=0.85)
        special_stage_enter_menu(self.serial)

class SpecialStageHandler(BaseStateHandler):
    def handle(self):
        wait_click(self.serial, MainView.BACK.value)

class PvpCloseHandler(BaseStateHandler): # 這還不是很精準
    def handle(self):
        wait_click(self.serial, MainView.CLOSE_PVP.value)

class BoardEndHandler(BaseStateHandler):
    def handle(self):
        wait_click(self.serial, MainView.CLOSE_BOARD2.value)

class SpecialOfferHandler(BaseStateHandler):
    def handle(self):
        wait_click(self.serial, MainView.CLOSE_BOARD2.value)

class RetryHandler(BaseStateHandler):
    def handle(self):
        if exist(self.serial, Retry.TEXT1.value):
            wait_click(self.serial, Retry.BTN.value)
        elif exist(self.serial, Retry.TEXT2.value):
            wait_click(self.serial, Retry.BTN.value)

class SeasonPassHandler(BaseStateHandler):
    def handle(self):
        wait_click(self.serial, Confirm.CANCEL.value)

class DONTShowAgainHandler(BaseStateHandler):
    def handle(self):
        wait_click(self.serial, MainView.BOARD_DONT_SHOW.value)
        wait_click(self.serial, MainView.CLOSE_BOARD2.value)

class ComebackHandler(BaseStateHandler):
    def handle(self):
        wait_click(self.serial, MainView.CLOSE_BOARD2.value)

class BuffEventHandler(BaseStateHandler):
    def handle(self):
        wait_click(self.serial, MainView.CLOSE_BOARD2.value)

class PolicyHandler(BaseStateHandler):
    def handle(self):
        wait_click(self.serial, MainView.CLOSE_BOARD2.value)

class UnknownHandler(BaseStateHandler):
    def handle(self):
        time.sleep(0.5)