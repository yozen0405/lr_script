
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

class PopUpHandler(BaseHandler):
    def __init__(self, context: GameContext):
        self.ctx = context
        self.auth_failed_count = 0
        self.popup_rules = [
            (GameView.AUTH_FAILED.value, Confirm.SMALL.value, 0.9, self._inc_auth_fail),
            (GameView.ENG_BTN.value, Confirm.SMALL.value, 0.9, None),
            (GameView.LINE_LOGIN_SUCCESS.value, Confirm.SMALL.value, 0.9, None),
            (GameView.GUEST_LOGIN_TEXT.value, GameView.GUEST_CONNECT.value, 0.9, None),
            (GameView.DOWNLOAD_TEXT.value, Confirm.SMALL.value, 0.9, None),
        ]

    def on_page(self) -> bool:
        for detect_img, _, thresh, _ in self.popup_rules:
            if exist(self.ctx.serial, detect_img, threshold=thresh):
                return True

        if exist(self.ctx.serial, GameView.ERROR_TEXT.value, threshold=0.9):
            return True
        
        return False

    def handle(self) -> bool:
        for detect_img, click_img, thresh, callback in self.popup_rules:
            if exist(self.ctx.serial, detect_img, threshold=thresh):
                if callback: callback()
                wait_click(self.ctx.serial, click_img)
                return

        if exist(self.ctx.serial, GameView.ERROR_TEXT.value, threshold=0.9):
            force_close(self.ctx.serial)
            return
        
        raise GameError("Unhandled Pop-Up")

    def _inc_auth_fail(self):
        self.auth_failed_count += 1
        if self.auth_failed_count >= 3:
            raise GameError("Auth Failed x3")