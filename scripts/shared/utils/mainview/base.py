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
from scripts.shared.events.season_pass.enum import SeasonPassImg
from scripts.shared.constants import MainView
from scripts.shared.events.special_stage.enum import SpecialStage
from scripts.shared.utils.mainview.handlers import (
    BaseStateHandler, TutorialHandler, SkipGuideHandler,
    PvpCloseHandler, UnknownHandler, BoardEndHandler,
    SpecialOfferHandler, RetryHandler, SeasonPassHandler,
    DONTShowAgainHandler, ComebackHandler, SpecialStageHandler,
    BuffEventHandler, PolicyHandler
)

class MainViewHandler:
    def __init__(self, serial):
        self.serial = serial
        
        self.strategies: dict[MainViewState, BaseStateHandler] = {
            MainViewState.TUTORIALS: TutorialHandler(serial),
            MainViewState.SKIP: SkipGuideHandler(serial),
            MainViewState.PVP_OPENED: PvpCloseHandler(serial),
            MainViewState.BOARD_END: BoardEndHandler(serial),
            MainViewState.COMEBACK: ComebackHandler(serial),
            MainViewState.SPECIAL_OFFERS: SpecialOfferHandler(serial),
            MainViewState.SPECIAL_STAGE: SpecialStageHandler(serial),
            MainViewState.RETRY: RetryHandler(serial),
            MainViewState.SEASON_PASS: SeasonPassHandler(serial),
            MainViewState.DONT_SHOW_AGAIN: DONTShowAgainHandler(serial),
            MainViewState.BUFF_EVENT: BuffEventHandler(serial),
            MainViewState.POLICY: PolicyHandler(serial),
            MainViewState.UNKNOWN: UnknownHandler(serial)
        }

    def _detect_state(self) -> MainViewState:
        if exist(self.serial, MainView.BOOSTER.value, threshold=0.96):
            return MainViewState.CLEAR

        if exist(self.serial, Retry.BTN.value, threshold=0.85):
            return MainViewState.RETRY
        
        if exist(self.serial, MainView.SKIP.value):
            return MainViewState.TUTORIALS
            
        if exist(self.serial, MainView.SKIP_2.value):
            return MainViewState.SKIP
            
        if exist(self.serial, MainView.CLOSE_PVP.value, threshold=0.9):
            return MainViewState.PVP_OPENED
        
        if exist(self.serial, MainView.BOARD_DONT_SHOW.value, threshold=0.9):
            return MainViewState.DONT_SHOW_AGAIN
        
        if exist(self.serial, MainView.BOARD_END.value, threshold=0.95):
            return MainViewState.BOARD_END
        
        if exist(self.serial, MainView.COMEBACK.value):
            return MainViewState.COMEBACK
        
        if exist(self.serial, MainView.SPECIAL_OFFERS.value):
            return MainViewState.SPECIAL_OFFERS
        
        if exist(self.serial, MainView.POLICY_TEXT.value):
            return MainViewState.POLICY
        
        if exist(self.serial, SeasonPassImg.POP_TEXT.value):
            return MainViewState.SEASON_PASS
        
        if exist(self.serial, SpecialStage.TEXT.value):
            return MainViewState.SPECIAL_STAGE

        if exist(self.serial, MainView.BUFF_EVENT.value):
            return MainViewState.BUFF_EVENT
        
        return MainViewState.UNKNOWN
    
    def detect_state(self) -> bool:
        current_state = self._detect_state()
        return current_state != MainViewState.UNKNOWN

    def run(self, timeout=150.0):
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            current_state = self._detect_state()
            
            if current_state == MainViewState.CLEAR:
                return

            handler = self.strategies.get(current_state)
            
            if handler:
                handler.handle()
            else:
                raise GameError("沒有對應的主畫面狀態處理器")
            
def on_main_view(serial):
    handler = MainViewHandler(serial)
    handler.run()