import time
import os
from core.system.logging.logger import log_msg
from core.actions.vision import wait_click, exist_click, exist, wait, wait_vanish, back, drag, get_pos, check_region_brightness
from core.base.exceptions import GameError
from scripts.shared.constants import MainView, Confirm, Retry
from scripts.shared.utils.mainview.enum import MainViewState
from scripts.shared.utils.hacks import apply_mode
import time
from abc import ABC, abstractmethod
from enum import Enum, auto
from core.actions.vision import wait_click, exist_click, exist, wait
from core.base.exceptions import GameError
from scripts.shared.events.season_pass.enum import SeasonPassImg
from scripts.shared.constants import MainView, GameView
from scripts.shared.events.special_stage.enum import SpecialStage
from scripts.shared.utils.mainview.interrupt.dimmed.base import DimmedStrategy
from scripts.shared.utils.mainview.interrupt.events.base import EventStrategy
from scripts.shared.controller.context import GameContext
from scripts.shared.events.pre_stage.base import on_pre_stage_page
from scripts.shared.events.main_stage.base import on_main_stage_page
from scripts.shared.events.main_stage.enum import MainStageImg
from scripts.shared.utils.mainview.rules import MainViewRules

class MainViewHandler():
    def __init__(self, context: GameContext):
        self.ctx = context
        
        self.dimmed_strategy = DimmedStrategy(self.ctx)
        self.event_strategy = EventStrategy(self.ctx)

        rule_factory = MainViewRules(self.ctx, self.dimmed_strategy, self.event_strategy)
        self.rules = sorted(rule_factory.get_all(), key=lambda x: x.priority)

    def on_page(self, strict: bool = True) -> bool:
        if exist(self.ctx.serial, MainView.AVATAR.value, threshold=0.95):
            return True
        if self.dimmed_strategy.on_no_avatar():
            return True
        if strict and on_pre_stage_page(self.ctx):
            return True
        return False

    def proccess(self, timeout=120.0) -> MainViewState:
        start_time = time.time()
        prev_state, cnt, max_cnt = None, 0, 3

        if not exist(self.ctx.serial, MainView.AVATAR.value, threshold=0.95):
            if on_pre_stage_page(self.ctx):
                return MainViewState.PRE_STAGE
            
            if on_main_stage_page(self.ctx):
                return MainViewState.MAIN_STAGE
        
        while time.time() - start_time < timeout:
            current_state = None
            
            for rule in self.rules:
                if rule.check():
                    log_msg(self.ctx.serial, f"目前正在主介面狀態: {rule.name}")
                    res = rule.action()
                    if res is not None:
                        current_state = res
                        break
                    else:
                        current_state = None 
                        break 

            if current_state is None:
                log_msg(self.ctx.serial, f"目前正在主介面狀態: {MainViewState.UNKNOWN.name}")
                current_state = MainViewState.UNKNOWN
            
            if current_state in [MainViewState.NONE, MainViewState.UNKNOWN]:
                if prev_state == current_state:
                    cnt += 1
                else:
                    prev_state, cnt = current_state, 0

                if current_state == MainViewState.UNKNOWN:
                    time.sleep(2.5)
                else:
                    time.sleep(1.5)
                
                if cnt >= max_cnt:
                    apply_mode(self.ctx.serial, mode_name="pre_stage", state="off")
                    if current_state == MainViewState.NONE:
                        return current_state
                    raise GameError("主介面狀態無法穩定，請檢查遊戲狀態。")
                
            if current_state in [MainViewState.TO_DOWNLOAD]:
                apply_mode(self.ctx.serial, mode_name="pre_stage", state="off")
                return current_state
            
            if current_state in [MainViewState.GAME_NOT_STARTED]:
                return current_state
            
            prev_state = current_state

        raise GameError("主介面偵測逾時，無法確認當前狀態。")
            
def on_main_view(context: GameContext, timeout=800.0):
    handler = MainViewHandler(context)
    return handler.proccess(timeout=timeout)

def is_on_main_view(context: GameContext, strict: bool = True) -> bool:
    handler = MainViewHandler(context)
    return handler.on_page(strict=strict)