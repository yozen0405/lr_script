import time
import os
from core.system.logger import log_msg
from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, back, drag, get_pos, check_region_brightness
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
from scripts.shared.utils.mainview.interrupt.dimmed.base import DimmedStrategy
from scripts.shared.utils.mainview.interrupt.no_avatar.base import NoAvatarStrategy
from scripts.shared.utils.mainview.interrupt.retry.base import RetryStrategy
from scripts.shared.utils.mainview.interrupt.base import BaseStrategy

# 目標進入到mainview以外的(若遊戲強制)介面，若否則停留在mainview

class MainViewHandler(BaseStrategy):
    def __init__(self, serial):
        self.serial = serial
        
        # 原則:有影響到我們的目標(例如在new acc就是打main stage), 就直接視為interrupt
        # 不管是點sheep要升級什麼的都算interrupt
        self.interrupt_strategies: dict[MainViewState, BaseStrategy] = {
            MainViewState.DIMMED: DimmedStrategy(serial),
            MainViewState.NO_AVATAR: NoAvatarStrategy(serial),
            MainViewState.RETRY: RetryStrategy(serial),
        }

    def _detect_state(self) -> MainViewState:
        if exist(self.serial, MainView.AVATAR.value, threshold=0.95):
            loc = get_pos(self.serial, MainView.AVATAR.value, threshold=0.95, return_center=False)
            if check_region_brightness(self.serial, region=loc):
                return MainViewState.CLEAR
            else:
                return MainViewState.DIMMED
            
        if self.interrupt_strategies[MainViewState.NO_AVATAR].check():
            return MainViewState.NO_AVATAR
        
        if self.interrupt_strategies[MainViewState.RETRY].check():
            return MainViewState.RETRY
        
        return MainViewState.UNKNOWN

    def check(self):
        current_state = self._detect_state()

        if current_state == MainViewState.UNKNOWN:
            return False
        
        if current_state == MainViewState.RETRY:
            return False
       
        return True

    def proccess(self, timeout=40.0):
        start_time = time.time()
        unkwown_count = 0
        
        while time.time() - start_time < timeout:
            current_state = self._detect_state()
            log_msg(self.serial, f"[MainViewHandler] 當前狀態: {current_state.name}")

            if current_state in self.interrupt_strategies:
                handler = self.interrupt_strategies[current_state]
                handler.proccess()
                continue
            
            if current_state == MainViewState.CLEAR: # 目前來說是這樣
                return
            
            if current_state == MainViewState.UNKNOWN:
                time.sleep(1.0)
                unkwown_count += 1
                if unkwown_count >= 2:
                    log_msg(self.serial, f"[MainViewHandler] 已經不在主畫面了，跳出")
                    return

        raise GameError(f"[MainViewHandler] 超過等待主畫面時間上限")
        
            
def on_main_view(serial, timeout=150.0):
    handler = MainViewHandler(serial)
    handler.proccess(timeout=timeout)

def is_on_main_view(serial) -> bool:
    handler = MainViewHandler(serial)
    return handler.check()