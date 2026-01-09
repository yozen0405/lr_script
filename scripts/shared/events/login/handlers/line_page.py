
import time
from abc import ABC, abstractmethod
from core.system.logging.logger import log_msg
from core.actions.vision import wait_click, exist_click, exist, wait, back, drag, check_freeze
from core.actions.system import force_close, force_close_line
from core.base.exceptions import GameError
from scripts.shared.constants import GameView, MainView, Confirm, Retry
from scripts.shared.events.login.enum import LoginState
from scripts.shared.controller.context import GameContext
from scripts.shared.events.login.handlers.base import BaseHandler

class LinePageHandler(BaseHandler):
    def __init__(self, context: GameContext):
        self.ctx = context

    def on_page(self) -> bool:
        return exist(self.ctx.serial, GameView.LINE_APP_TEXT_3.value, threshold=0.9) or \
                exist(self.ctx.serial, GameView.LINE_APP_TEXT.value, threshold=0.9) or \
                exist(self.ctx.serial, GameView.LINE_APP_TEXT_4.value, threshold=0.9)
    
    def handle(self):
        if not wait(self.ctx.serial, GameView.LINE_APP_TEXT_2.value, threshold=0.9):
            force_close_line(self.ctx.serial, timeout=3.0)
            return
        for _ in range(4):
            drag(self.ctx.serial, (470, 520), (470, 220), duration=400, wait_time=1.5)
            if exist_click(self.ctx.serial, GameView.LINE_APP_ALLOW_BTN.value, threshold=0.9):
                return