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
from scripts.shared.utils.mainview.interrupt.events.base import EventStrategy
from scripts.shared.controller.context import GameContext
from scripts.shared.events.pre_stage.base import on_pre_stage_page
from scripts.shared.events.main_stage.selector import on_main_stage_page
from scripts.shared.events.main_stage.enum import MainStage

class MainViewHandler():
    def __init__(self, context: GameContext):
        self.ctx = context
        
        self.dimmed_strategy = DimmedStrategy(self.ctx)
        self.no_avatar_strategy = NoAvatarStrategy(self.ctx)
        self.event_strategy = EventStrategy(self.ctx)

    def on_page(self, strict: bool = True) -> bool:
        if exist(self.ctx.serial, MainView.AVATAR.value, threshold=0.95):
            return True
        if self.no_avatar_strategy.handle_supported():
            return True
        if strict and on_pre_stage_page(self.ctx):
            return True
        return False

    def proccess(self, timeout=120.0) -> MainViewState:
        start_time = time.time()

        if on_pre_stage_page(self.ctx):
            return MainViewState.PRE_STAGE
        
        if on_main_stage_page(self.ctx):
            return MainViewState.MAIN_STAGE

        prev_state = None
        cnt = 0 # the time that stable state maintained
        max_cnt = 3

        def update_state(state: MainViewState):
            nonlocal prev_state, cnt, max_cnt, start_time, timeout
            log_msg(self.ctx.serial, f"Main View 偵測到狀態: {state.name}")
            if state == MainViewState.NONE or \
               state == MainViewState.UNKNOWN:
                max_cnt = 3
            else:
                max_cnt = 2
                timeout = 240.0
                start_time = time.time()

            if prev_state != state:
                prev_state = state
                cnt = 0
            else:
                cnt += 1
        
        while time.time() - start_time < timeout:
            if cnt >= max_cnt:
                return prev_state
            
            if exist(self.ctx.serial, Retry.TEXT1.value, threshold=0.8) or \
                exist(self.ctx.serial, Retry.TEXT2.value, threshold=0.8):
                exist_click(self.ctx.serial, Retry.BTN.value, threshold=0.8)
                continue

            if exist(self.ctx.serial, MainView.AVATAR.value, threshold=0.95):
                loc = get_pos(self.ctx.serial, MainView.AVATAR.value, threshold=0.95, return_center=False)

                if check_region_brightness(self.ctx.serial, region=loc):
                    if exist(self.ctx.serial, MainStage.BTN.value, threshold=0.9):
                        update_state(MainViewState.NONE)
                        continue
                    elif exist(self.ctx.serial, MainView.LEVEL_POP_TEXT.value, threshold=0.95):
                        wait_click(self.ctx.serial, MainView.CLOSE_BOARD_YELLOW.value, threshold=0.9)
                        continue
                    else:
                        update_state(MainViewState.UNKNOWN)
                        continue
                elif self.dimmed_strategy.handle_supported():
                    continue
                else:
                    state = self.event_strategy.detect()
                    
                    if state == MainViewState.TO_DOWNLOAD:
                        return MainViewState.TO_DOWNLOAD
                    elif state != MainViewState.UNKNOWN:
                        self.event_strategy.handle_event(state)
                        update_state(state)
                    else:
                        update_state(MainViewState.UNKNOWN)
                    continue
                
            if self.no_avatar_strategy.handle_supported():
                continue
            else:
                update_state(MainViewState.UNKNOWN)
                continue
        return MainViewState.UNKNOWN
            
def on_main_view(context: GameContext, timeout=150.0):
    handler = MainViewHandler(context)
    handler.proccess(timeout=timeout)

def is_on_main_view(context: GameContext, strict: bool = True) -> bool:
    handler = MainViewHandler(context)
    return handler.on_page(strict=strict)