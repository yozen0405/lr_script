import time
from abc import ABC, abstractmethod
from core.system.logger import log_msg
from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, back, drag, check_freeze
from core.actions.system import force_close, force_close_line
from core.base.exceptions import GameError
from scripts.shared.utils.retry import connection_retry
from scripts.shared.utils.game_boot import open_game
from scripts.shared.utils.mainview.base import is_on_main_view
from scripts.shared.constants import GameView, MainView, Confirm, Retry
from scripts.shared.events.login.enum import LoginState

class LoginStrategy(ABC):
    def __init__(self, serial):
        self.serial = serial
        self.max_retries = 3
        self.max_unknowns = 3
        self.current_state = LoginState.GAME_NOT_STARTED

    def process(self, mode: str):
        """
        look --> think --> act
        """
        log_msg(self.serial, "開始登入流程")
        retry_count = 0
        unkwown_count = 0
        
        while True:
            try:
                current_state = self.detect_state()
                log_msg(self.serial, f"當前狀態: {current_state.name}")

                if current_state == LoginState.GAME_NOT_STARTED:
                    unkwown_count = 0
                    open_game(self.serial, mode)
                
                elif current_state == LoginState.LOGIN_METHOD_PAGE:
                    unkwown_count = 0
                    self.handle_login_page()
                
                elif current_state == LoginState.TERMS_AGREEMENT_PAGE:
                    unkwown_count = 0
                    self.handle_terms_agreement()
                
                elif current_state == LoginState.LINE_APP_PAGE:
                    unkwown_count = 0
                    self.handle_line_app_page()
                
                elif current_state == LoginState.LOADING_PAGE:
                    unkwown_count = 0
                    self.handle_loading_page()
                
                elif current_state == LoginState.RETRY:
                    unkwown_count = 0
                    self.handle_retry()

                elif current_state == LoginState.POPUP: # 也有可能誤判，其實是 in game
                    unkwown_count = 0
                    if not self.handle_popup():
                        log_msg(self.serial, "登入流程完成")
                        break

                elif current_state == LoginState.IN_GAME:
                    log_msg(self.serial, "登入流程完成")
                    break

                elif current_state == LoginState.UNKNOWN:
                    self.handle_unknown_state()
                    unkwown_count += 1
                    if unkwown_count >= self.max_unknowns:
                        log_msg(self.serial, "無法辨識當前狀態，重啟遊戲")
                        force_close(self.serial)
                        unkwown_count = 0
                        retry_count += 1

            except GameError as e:
                log_msg(self.serial, f"發生錯誤: {e}, 重試中...")
                retry_count += 1
                force_close(self.serial)

            if retry_count >= self.max_retries:
                raise GameError("登入流程重試次數過多，終止執行")
                

    def detect_state(self) -> LoginState:
        if exist(self.serial, GameView.ICON.value):
            return LoginState.GAME_NOT_STARTED
        elif exist(self.serial, Retry.TEXT1.value) or exist(self.serial, Retry.TEXT2.value):
            return LoginState.RETRY
        elif exist(self.serial, MainView.BOARD_END.value, threshold=0.95):
            return LoginState.POPUP
        elif exist(self.serial, GameView.WAITING.value, threshold=0.9):
            return LoginState.LOGIN_METHOD_PAGE
        elif exist(self.serial, GameView.LINE_GAME_TEXT.value, threshold=0.95):
            return LoginState.TERMS_AGREEMENT_PAGE
        elif exist(self.serial, GameView.LINE_APP_TEXT.value, threshold=0.9) or \
           exist(self.serial, GameView.LINE_WEBSITE.value, threshold=0.9) or \
           exist(self.serial, GameView.LINE_APP_TEXT_3.value, threshold=0.9):
            return LoginState.LINE_APP_PAGE
        elif exist(self.serial, GameView.LOADING.value):
            return LoginState.LOADING_PAGE
        elif is_on_main_view(self.serial):
            return LoginState.IN_GAME
        else:
            return LoginState.UNKNOWN
    
    @abstractmethod
    def handle_line_app_page(self) -> LoginState:
        """
        子類別必須實作此方法。
        """
        pass
    
    def handle_popup(self) -> bool:
        if exist(self.serial, GameView.AUTH_FAILED.value):
            wait_click(self.serial, Confirm.SMALL.value)
            return True
            
        if exist(self.serial, GameView.ENG_BTN.value):
            wait_click(self.serial, Confirm.SMALL.value)
            return True
            
        if exist(self.serial, GameView.LINE_LOGIN_SUCCESS.value):
            wait_click(self.serial, Confirm.SMALL.value)
            return True
            
        if exist(self.serial, GameView.GUEST_LOGIN_TEXT.value):
            wait_click(self.serial, GameView.GUEST_CONNECT.value, threshold=0.9)
            return True
            
        if exist(self.serial, GameView.DOWNLOAD_TEXT.value, threshold=0.9):
            wait_click(self.serial, Confirm.SMALL.value)
            return True

        return False

    def handle_login_page(self):
        if exist_click(self.serial, GameView.GUEST_LOGIN_BTN.value, threshold=0.9):
            pass

        if exist_click(self.serial, GameView.PLAY_BTN.value):
            pass
        
        if exist_click(self.serial, GameView.LOGIN_LINE.value):
            pass

    def handle_retry(self):
        if exist(self.serial, Retry.TEXT1.value):
            wait_click(self.serial, Retry.BTN.value)

    def handle_unknown_state(self):
        time.sleep(1.0)

    def handle_terms_agreement(self):
        for _ in range(10):
            if exist(self.serial, GameView.TERMS_COMPLETE.value, threshold=0.99):
                break
            exist_click(self.serial, GameView.TERMS.value, threshold=0.5)
        wait_click(self.serial, GameView.AGREE_TERMS.value, threshold=0.5)

    def handle_loading_page(self):
        if check_freeze(self.serial):
            log_msg(self.serial, "Loading 畫面凍結，重啟遊戲")
            force_close(self.serial)

class GuestLoginStrategy(LoginStrategy):
    def __init__(self, serial):
        super().__init__(serial)

    def handle_line_app_page(self) -> LoginState:
        force_close_line(self.serial, timeout=3.0)
        
        if wait(self.serial, GameView.LINE_WEBSITE.value, timeout=3.0):
            for _ in range(3):
                back(self.serial)

class LineLoginStrategy(LoginStrategy):
    def __init__(self, serial):
        super().__init__(serial)

    def handle_line_app_page(self) -> LoginState:
        wait(self.serial, GameView.LINE_APP_TEXT_2.value, threshold=0.9)
        for _ in range(4):
            drag(self.serial, (100, 600), (100, 150))
        wait_click(self.serial, GameView.LINE_APP_ALLOW_BTN.value, threshold=0.9)


def first_guest_login(serial):
    strategy = GuestLoginStrategy(serial)
    strategy.process(mode="pre_stage")

def guest_login(serial, mode: str = "main_stage"):
    strategy = GuestLoginStrategy(serial)
    strategy.process(mode=mode)

def line_login(serial, mode: str = ""):
    strategy = LineLoginStrategy(serial)
    strategy.process(mode=mode)