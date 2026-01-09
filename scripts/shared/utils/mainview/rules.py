from dataclasses import dataclass
from typing import Callable, Optional, List
from core.actions.vision import check_region_brightness
from core.actions.vision import exist, exist_click, get_pos, wait_click
from core.base.exceptions import GameError
from core.system.logging.logger import log_msg
from scripts.shared.constants import Retry, Confirm
from scripts.shared.constants.view import GameView, MainView
from scripts.shared.controller.context import GameContext
from scripts.shared.events.main_stage.enum import MainStageImg
from scripts.shared.utils.hacks import apply_mode
from scripts.shared.utils.mainview.enum import MainViewState
from scripts.shared.utils.mainview.interrupt.dimmed.base import DimmedStrategy
from scripts.shared.utils.mainview.interrupt.events.base import EventStrategy

@dataclass
class ViewRule:
    name: str
    check: Callable[[], bool]
    # action 回傳 Optional[MainViewState]。如果回傳 None，代表「已處理障礙，請重新偵測」
    action: Callable[[], Optional[MainViewState]]
    priority: int = 10

class MainViewRules:
    def __init__(self, context: GameContext, dimmed: DimmedStrategy, event: EventStrategy):
        self.ctx = context
        self.dimmed_strategy: DimmedStrategy = dimmed
        self.event_strategy: EventStrategy = event
    
    def get_all(self) -> List[ViewRule]:
        return [
            ViewRule("網路重試", self._check_retry, self._handle_retry, priority=1),
            ViewRule("正常主介面", self._check_main_view, self._handle_main_view, priority=2),
            ViewRule("變暗狀態", self._check_dimmed, self._handle_dimmed, priority=3),
             ViewRule("遊戲未啟動", self._check_game_not_started, self._handle_game_not_started, priority=4),
            ViewRule("無大頭貼狀態", self._check_no_avatar, self._handle_no_avatar, priority=5),
        ]

    def _check_retry(self):
        return exist(self.ctx.serial, Retry.TEXT1.value, threshold=0.8) or \
               exist(self.ctx.serial, Retry.TEXT2.value, threshold=0.8)

    def _handle_retry(self):
        if not exist_click(self.ctx.serial, Retry.BTN.value, threshold=0.8):
            exist_click(self.ctx.serial, Confirm.SMALL.value)
        return None 

    def _check_main_view(self):
        loc = get_pos(self.ctx.serial, MainView.AVATAR.value, threshold=0.9, return_center=False)
        if loc:
            return check_region_brightness(self.ctx.serial, region=loc)
        return False
    
    def _handle_main_view(self):
        if exist(self.ctx.serial, MainView.LEVEL_POP_TEXT.value, threshold=0.95):
            wait_click(self.ctx.serial, MainView.CLOSE_BOARD_YELLOW.value, threshold=0.9)
            return MainViewState.PENDING
        return MainViewState.NONE
    
    def _check_dimmed(self):
        loc = get_pos(self.ctx.serial, MainView.AVATAR.value, threshold=0.9, return_center=False)
        if loc:
            return not check_region_brightness(self.ctx.serial, region=loc)
        return False

    def _handle_dimmed(self):
        if exist(self.ctx.serial, MainStageImg.BTN.value):
            if self.dimmed_strategy.handle_skip():
                return MainViewState.PENDING
            return self._handle_events()
        
        if self.dimmed_strategy.handle_board() != MainViewState.UNKNOWN:
            return self.dimmed_strategy.handle_board()
    
        if self.dimmed_strategy.handle_supported():
            return MainViewState.PENDING
        
        if self.event_strategy.handle_special_stage():
            return MainViewState.SPECIAL_STAGE

        return MainViewState.UNKNOWN

    def _handle_events(self):
        apply_mode(self.ctx.serial, mode_name="pre_stage", state="on")
        state = self.event_strategy.detect_main()
        if state != MainViewState.UNKNOWN:
            self.event_strategy.handle_main_event(state)
            return state
        return MainViewState.UNKNOWN
    
    def _check_no_avatar(self):
        return exist(self.ctx.serial, MainView.AVATAR.value, threshold=0.9) is False
    
    def _handle_no_avatar(self):
        if self.dimmed_strategy.handle_supported():
            return MainViewState.PENDING
        else:
            return MainViewState.UNKNOWN
        
    def _check_game_not_started(self):
        return exist(self.ctx.serial, GameView.ICON.value)
    
    def _handle_game_not_started(self):
        return MainViewState.GAME_NOT_STARTED