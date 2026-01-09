
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

class RetryHandler(BaseHandler):
    def __init__(self, context: GameContext):
        self.ctx = context

    def on_page(self) -> bool:
        return exist(self.ctx.serial, Retry.TEXT1.value) or exist(self.ctx.serial, Retry.TEXT2.value)
    
    def handle(self):
        if exist(self.ctx.serial, Retry.BTN.value):
            exist_click(self.ctx.serial, Retry.BTN.value)
        elif exist(self.ctx.serial, Confirm.SMALL.value):
            exist_click(self.ctx.serial, Confirm.SMALL.value)
