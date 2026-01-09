import time
from core.system.logging.logger import log_msg
from core.actions.vision import wait_click, exist_click, exist, wait, back, drag, check_freeze, wait_vanish
from core.actions.system import force_close, force_close_line
from core.base.exceptions import GameError
from scripts.shared.utils.mainview.base import is_on_main_view
from scripts.shared.constants import GameView, MainView, Confirm, Retry
from scripts.shared.events.login.enum import LoginState
from scripts.shared.controller.context import GameContext
from scripts.shared.events.login.handlers.base import BaseHandler

class OpenGameHandler(BaseHandler):
    def __init__(self, context: GameContext):
        self.ctx = context

    def on_page(self) -> bool:
        return exist(self.ctx.serial, GameView.ICON.value)
    
    def handle(self):
        succ = False
        on_open = 0
        while True:
            if exist_click(self.ctx.serial, GameView.ICON.value):
                on_open = 0

            if exist(self.ctx.serial, GameView.GAME_OPENED.value):
                on_open = 0
                if not wait_vanish(self.ctx.serial, GameView.GAME_OPENED.value, threshold=0.5, timeout=15.0):
                    log_msg(self.ctx.serial, "遊戲卡在開啟畫面，嘗試重新啟動...")
                    force_close(self.ctx.serial)
                    continue

            if exist_click(self.ctx.serial, GameView.PERM.value):
                on_open = 0

            if exist_click(self.ctx.serial, GameView.LINE_STUDIO_TEXT.value):
                on_open = 0
            
            if exist(self.ctx.serial, GameView.LOADING.value):
                succ = True
                break
            
            if exist(self.ctx.serial, GameView.WAITING.value):
                succ = True
                break
            
            on_open += 1
            if on_open >= 2:
                succ = True
                break
        
        if succ:
            pass
        else:
            raise GameError("遊戲啟動卡住多次，重啟無效")