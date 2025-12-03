import time
from abc import ABC, abstractmethod
from core.system.logger import log_msg
from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, back, drag, check_freeze
from core.actions.system import force_close, force_close_line
from core.base.exceptions import GameError
from scripts.shared.utils.retry import connection_retry
from scripts.shared.utils.game_boot import open_game
from scripts.shared.constants import GameView, MainView, Confirm, Retry
from scripts.shared.events.login.enum import LoginState

class LoginStrategy(ABC):
    def __init__(self, serial):
        self.serial = serial
        self.max_retries = 3
        self.current_state = LoginState.GAME_NOT_STARTED

    @abstractmethod
    def execute_login_action(self) -> LoginState:
        """
        子類別必須實作此方法。
        """
        pass

    def process(self, mode: str):
        """
        標準登入模板流程
        """
        retry_count = 0
        while True:
            if self.current_state == LoginState.GAME_NOT_STARTED:
                open_game(self.serial, mode)
            elif self.current_state == LoginState.ON_LOGIN_METHOD_PAGE:
                self.current_state = self._on_login_method_page()
                continue
            elif self.current_state == LoginState.ON_LOADING_PAGE:
                self.current_state = self._wait_for_loading_completion()
                continue
            elif self.current_state == LoginState.ON_TERMS_AGREEMENT_PAGE:
                self._handle_terms_agreement()
            elif self.current_state == LoginState.ON_LINE_APP:
                self.current_state = self.execute_login_action()
                continue
            elif self.current_state == LoginState.IN_GAME:
                break
            self.current_state = self.current_state.next()

        if retry_count >= self.max_retries:
            raise GameError(f"{self.__class__.__name__} 登入動作失敗")
        log_msg(self.serial, "登入流程完成")

    def _on_login_method_page(self) -> LoginState:
        cnt = 0
        for _ in range(10):
            if wait(self.serial, GameView.WAITING.value, timeout=3.0) or wait(self.serial, GameView.WAITING_2.value, timeout=3.0): # 在選擇登入方式頁面
                cnt = 0
                if exist(self.serial, GameView.AUTH_FAILED.value): # 認證失敗
                    wait_click(self.serial, Confirm.SMALL.value)
                    return LoginState.ON_LOGIN_METHOD_PAGE

                if exist(self.serial, Retry.TEXT1.value): # Retry 彈窗
                    wait_click(self.serial, Confirm.SMALL.value, wait_time=2.0)
                    wait_click(self.serial, GameView.PLAY_BTN.value, timeout=3.0)
                    continue

                if exist(self.serial, GameView.PLAY_BTN.value): # Play btn
                    wait_click(self.serial, GameView.PLAY_BTN.value)
                    connection_retry(self.serial, appear=GameView.LOADING.value, timeout=40.0)
                    return LoginState.ON_LOADING_PAGE
                
                if exist(self.serial, GameView.LOGIN_LINE.value): # 條款頁面
                    exist_click(self.serial, GameView.LOGIN_LINE.value)
                    return LoginState.ON_TERMS_AGREEMENT_PAGE
                
                if exist(self.serial, GameView.ENG_BTN.value): # 語言選擇頁面
                    wait_click(self.serial, Confirm.SMALL.value)
                    connection_retry(self.serial, appear=GameView.LOADING.value, timeout=40.0)
                    return LoginState.ON_LOADING_PAGE

                # 成功登入頁面 ( mising guest login success)
                if exist(self.serial, GameView.LINE_LOGIN_SUCCESS.value): # Line 登入成功頁面
                    wait_click(self.serial, Confirm.SMALL.value)
                    continue

            elif exist(self.serial, GameView.LOADING.value): # 已經進入 Loading 頁面
                cnt = 0
                return LoginState.ON_LOADING_PAGE
            else:
                cnt += 1
                if cnt >= 2:
                    return LoginState.IN_GAME # 這邊不是很嚴謹
            
        if exist(self.serial, GameView.ICON.value):
            return LoginState.GAME_NOT_STARTED
        raise GameError("無法判斷當前登入頁面狀態")

    def _handle_terms_agreement(self):
        """處理條款同意流程"""
        if not wait(self.serial, GameView.LINE_GAME_TEXT.value, threshold=0.5, timeout=10.0):
            raise GameError("無法進入條款同意頁面")

        log_msg(self.serial, "檢測到條款，開始同意流程...")
        for _ in range(15):
            if exist(self.serial, GameView.TERMS_COMPLETE.value, threshold=0.99):
                break
            exist_click(self.serial, GameView.TERMS.value, threshold=0.5)

        if not exist(self.serial, GameView.TERMS_COMPLETE.value, threshold=0.99):
            raise GameError("條款認證失敗：無法勾選所有條款")

        wait_click(self.serial, GameView.AGREE_TERMS.value, threshold=0.5)

    def _wait_for_loading_completion(self, timeout: float = 900.0) -> LoginState:
        """處理 Loading 條、下載資源、Retry 彈窗"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # 正在 Loading Page
            if wait(self.serial, GameView.LOADING.value, timeout=3.0):
                self._handle_popups_during_loading()
            elif exist(self.serial, GameView.ICON.value):
                return LoginState.GAME_NOT_STARTED
            else: # 不太好的方法，但目前只能這樣判斷了
                return LoginState.IN_GAME
            
            if exist(self.serial, Retry.TEXT1.value):
                wait_click(self.serial, Retry.BTN.value, wait_time=1.0)
                start_time = time.time() 
                continue

            if check_freeze(self.serial):
                force_close(self.serial)
                time.sleep(1.5)
                return LoginState.GAME_NOT_STARTED
                
            time.sleep(1.0)
            
        raise GameError("登入 Timeout：卡在 Loading 過久")

    def _handle_popups_during_loading(self):
        """處理 Loading 過程中的突發彈窗 (下載確認、錯誤重試)"""
        if exist(self.serial, Confirm.SMALL.value, threshold=0.8):
            if not exist(self.serial, GameView.DOWNLOAD_TEXT.value):
                wait_click(self.serial, Confirm.SMALL.value)
                wait_click(self.serial, GameView.PLAY_BTN.value, timeout=25.0, wait_time=3.0)
            else:
                wait_click(self.serial, Confirm.SMALL.value, threshold=0.9)

class GuestLoginStrategy(LoginStrategy):
    def __init__(self, serial):
        super().__init__(serial)

        self.guest_login_retries = 0
        self.max_guest_login_retries = 4
    
    def execute_login_action(self) -> LoginState:
        """
        嘗試點擊訪客登入。
        """
        if not self._do_line_app_job():
            force_close(self.serial)
            self.guest_login_retries = 0
            return LoginState.GAME_NOT_STARTED

        if self.guest_login_retries >= self.max_guest_login_retries:
            force_close(self.serial)
            time.sleep(1.5)
            return LoginState.GAME_NOT_STARTED

        if not exist_click(self.serial, GameView.GUEST_LOGIN.value, threshold=0.5):
            self.guest_login_retries += 1

        return LoginState.ON_LOGIN_METHOD_PAGE


    def _do_line_app_job(self):
        """
        目的是為了讓隱藏的 Guest 按鈕出現
        """
        if not wait(self.serial, GameView.LINE_APP_TEXT.value, timeout=15.0):
            log_msg(self.serial, "找不到 Line App 驗證頁面")
            return False

        force_close_line(self.serial, timeout=3.0)
        
        if wait(self.serial, GameView.LINE_WEBSITE.value, timeout=15.0):
            for _ in range(3):
                back(self.serial)
        return True

class LineLoginStrategy(LoginStrategy):
    def __init__(self, serial):
        super().__init__(serial)

        self.login_retries = 0
        self.max_login_retries = 3

    def execute_login_action(self) -> LoginState:
        if not wait(self.serial, GameView.LINE_APP_TEXT.value, timeout=15.0):
            if exist(self.serial, GameView.LINE_WEBSITE.value):
                raise GameError("你沒有登入 Line App，無法使用 Line 登入遊戲")
            self.login_retries += 1
            force_close_line(self.serial)
            time.sleep(1.5)
            return LoginState.ON_LOGIN_METHOD_PAGE
        
        if self.login_retries >= self.max_login_retries:
            raise GameError("多次嘗試 Line 登入失敗")

        wait(self.serial, GameView.LINE_APP_TEXT_2.value, threshold=0.9)
        for _ in range(4):
            drag(self.serial, (100, 600), (100, 150))
            
        wait_click(self.serial, GameView.LINE_APP_ALLOW_BTN.value, threshold=0.9)

        return LoginState.ON_LOGIN_METHOD_PAGE


def first_guest_login(serial):
    strategy = GuestLoginStrategy(serial)
    strategy.process(mode="pre_stage")

def guest_login(serial, mode: str = "main_stage"):
    strategy = GuestLoginStrategy(serial)
    strategy.process(mode=mode)

def line_login(serial, mode: str = ""):
    strategy = LineLoginStrategy(serial)
    strategy.process(mode=mode)