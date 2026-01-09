from typing import Dict, Type, Optional
from core.system.logging.logger import log_msg
from core.base.exceptions import GameError
from scripts.shared.utils.mainview.base import on_main_view
from scripts.shared.utils.mainview.enum import MainViewState
from scripts.shared.controller.context import GameContext
from .base import StateResolver
from .resolvers import LoginResolver, PreStageResolver, DownloadResolver

class LifecycleManager:
    def __init__(self, context: GameContext):
        self.ctx = context

        self.resolvers: Dict[MainViewState, StateResolver] = {
            MainViewState.GAME_NOT_STARTED: LoginResolver(),
            MainViewState.PRE_STAGE:        PreStageResolver(),
            MainViewState.TO_DOWNLOAD:      DownloadResolver(),
        }

    def ensure_main_view(self) -> MainViewState:
        success_states = {MainViewState.MAIN_STAGE, MainViewState.NONE}

        for i in range(8):
            log_msg(self.ctx.serial, f"[Lifecycle] 檢查遊戲狀態")
            
            current_state = on_main_view(self.ctx)

            if current_state in success_states:
                log_msg(self.ctx.serial, f"[Lifecycle] 確認在目標狀態: {current_state.name}")
                return current_state

            resolver = self.resolvers.get(current_state)
            if resolver:
                log_msg(self.ctx.serial, f"[Lifecycle] 處理狀態: {current_state.name}")
                resolver.resolve(self.ctx)
            
            log_msg(self.ctx.serial, f"[Lifecycle] 未知或無法處理的狀態: {current_state.name}，重試中...")

        log_msg(self.ctx.serial, "[Lifecycle] 無法將遊戲帶到主畫面")
        raise GameError("無法進入主畫面")

def ensure_main_view(context: GameContext) -> MainViewState:
    manager = LifecycleManager(context)
    return manager.ensure_main_view()