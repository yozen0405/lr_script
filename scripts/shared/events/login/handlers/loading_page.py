
import time
from abc import ABC, abstractmethod
from core.system.logging.logger import log_msg
from core.actions.vision import wait_click, exist_click, exist, wait, back, drag, check_freeze
from core.actions.system import force_close, force_close_line
from core.base.exceptions import GameError
from scripts.shared.utils.mainview.base import is_on_main_view
from scripts.shared.constants import GameView, MainView, Confirm, Retry
from scripts.shared.events.login.enum import LoginState
from scripts.shared.controller.context import GameContext
from scripts.shared.events.login.handlers.base import BaseHandler

class LoadingPageHandler(BaseHandler):
    def __init__(self, context: GameContext):
        self.ctx = context
        self.freeze_times = 0

    def on_page(self) -> bool:
        return exist(self.ctx.serial, GameView.LOADING.value)
    
    def handle(self):
        if check_freeze(self.ctx.serial):
            self.freeze_times += 1
            if self.freeze_times >= 2:
                log_msg(self.ctx.serial, "Loading 畫面凍結，重啟遊戲")
                self.freeze_times = 0
                force_close(self.ctx.serial)