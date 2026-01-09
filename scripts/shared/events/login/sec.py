import time
from abc import ABC, abstractmethod
from core.system.logging.logger import log_msg
from core.actions.vision import wait_click, exist_click, exist, wait, back, drag, check_freeze
from core.actions.system import force_close, force_close_line
from core.base.exceptions import GameError
from scripts.shared.events.login.handlers.apple_page import ApplePageHandler
from scripts.shared.events.login.handlers.loading_page import LoadingPageHandler
from scripts.shared.events.login.handlers.login_apple import LoginAppleHandler
from scripts.shared.events.login.handlers.pop_up import PopUpHandler
from scripts.shared.events.login.handlers.terms import TermsHandler
from scripts.shared.events.login.handlers.retry import RetryHandler
from scripts.shared.events.login.handlers.open_game import OpenGameHandler
from scripts.shared.events.login.handlers.login_line import LoginLineHandler
from scripts.shared.events.login.handlers.line_page import LinePageHandler
from scripts.shared.events.login.handlers.confirm_perm import ConfirmPermHandler
from scripts.shared.utils.mainview.base import is_on_main_view
from scripts.shared.constants import GameView, MainView, Confirm, Retry
from scripts.shared.events.login.enum import LoginState
from scripts.shared.controller.context import GameContext
from scripts.shared.events.login.handlers.base import BaseHandler

class LoginStrategy(ABC):
    def __init__(self, context: GameContext):
        self.ctx = context
        
        self.popup_handler = PopUpHandler(context)
        self.terms_handler = TermsHandler(context)
        self.loading_handler = LoadingPageHandler(context)
        self.retry_handler = RetryHandler(context)
        self.open_game_handler = OpenGameHandler(context)
        self.confirm_perm = ConfirmPermHandler(context)
        
        self.handler_map: dict[LoginState, BaseHandler] = {
            LoginState.GAME_NOT_STARTED: self.open_game_handler,
            LoginState.RETRY: self.retry_handler,
            LoginState.POP_UP: self.popup_handler,
            LoginState.LOADING_PAGE: self.loading_handler,
            LoginState.TERMS_AGREEMENT_PAGE: self.terms_handler,
            LoginState.CONFIRM_PERM: self.confirm_perm,
        }

    def process(self):
        log_msg(self.ctx.serial, f"啟動 {self.__class__.__name__} 流程")

        start_time = time.time()
        unknown_count = 0

        while time.time() - start_time < 500:
            current_state = None
            has_err = False
            for state, cls in self.handler_map.items():
                if cls.on_page():
                    current_state = state
                    log_msg(self.ctx.serial, f"偵測到狀態: {state.name}，啟動對應處理程序")
                    try:
                        cls.handle()
                    except GameError as e:
                        log_msg(self.ctx.serial, f"[Login] 處理程序錯誤: {e}")
                        has_err = True
                    break

            if current_state is None:
                if is_on_main_view(self.ctx):
                    log_msg(self.ctx.serial, "已進入主畫面，登入流程完成")
                    return
                
                unknown_count += 1
                log_msg(self.ctx.serial, f"無法辨識當前狀態，未知次數: {unknown_count}")
                time.sleep(0.5)
            elif not has_err:
                unknown_count = 0

            if unknown_count >= 5:
                log_msg(self.ctx.serial, "未知狀態次數過多，強制重啟遊戲")
                force_close(self.ctx.serial)
                unknown_count = 0

        raise GameError(f"登入重試次數達上限, 當前 unknown count: {unknown_count}")
            
class GuestLoginStrategy(LoginStrategy):
    def __init__(self, context: GameContext):
        super().__init__(context)

        self.apple_login = LoginAppleHandler(context)
        self.apple_page = ApplePageHandler(context)

        self.handler_map.update({
            LoginState.LOGIN_METHOD_PAGE: self.apple_login,
            LoginState.LINE_APP_PAGE: self.apple_page, 
        })

class LineLoginStrategy(LoginStrategy):
    def __init__(self, context: GameContext):
        super().__init__(context)

        self.line_login = LoginLineHandler(context)
        self.line_page = LinePageHandler(context)

        self.handler_map.update({
            LoginState.LOGIN_METHOD_PAGE: self.line_login,
            LoginState.LINE_APP_PAGE: self.line_page, 
        })

def guest_login(context: GameContext):
    strategy = GuestLoginStrategy(context=context)
    strategy.process()

def line_login(context: GameContext):
    strategy = LineLoginStrategy(context=context)
    strategy.process()