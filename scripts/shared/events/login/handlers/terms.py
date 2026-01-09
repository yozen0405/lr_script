
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

class TermsHandler(BaseHandler):
    def __init__(self, context: GameContext):
        self.ctx = context

    def on_page(self) -> bool:
        return exist(self.ctx.serial, GameView.TERMS_PAGE_TEXT.value, threshold=0.9)

    def handle(self):
        succ = False
        start_time = time.time()
        while time.time() - start_time < 60:
            if not exist(self.ctx.serial, GameView.TERMS_PAGE_TEXT.value, threshold=0.9):
                return

            if exist(self.ctx.serial, GameView.TERMS_COMPLETE.value, threshold=0.97):
                succ = True
                break
            exist_click(self.ctx.serial, GameView.TERMS.value, threshold=0.9, wait_time=1.0)

        if not succ:
            raise GameError("同意使用條款失敗")
        wait_click(self.ctx.serial, GameView.AGREE_TERMS.value)