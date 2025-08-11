import time
from core.system.logger import log_msg
from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, back, drag, force_close, force_close_line
from core.base.exceptions import GameError
from scripts.shared.utils.retry import connection_retry
from scripts.shared.utils.game_boot import open_game
from scripts.shared.constants import GameView, MainView, Confirm, Retry

class BaseLoginFlow:
    def __init__(self, serial):
        self.serial = serial

    def _agree_terms(self):
        wait(self.serial, GameView.LINE_GAME_TEXT, threshold=0.5, timeout=30.0)

        for _ in range(15):
            if exist(self.serial, GameView.TERMS_COMPLETE, threshold=0.99):
                break
            exist_click(self.serial, GameView.TERMS, threshold=0.5)

        if not exist(self.serial, GameView.TERMS_COMPLETE, threshold=0.99):
            raise GameError("條款認證失敗")

        wait_click(self.serial, GameView.AGREE_TERMS, threshold=0.5)

    def _trigger_guest_btn(self):
        for attempt in range(1, 5):
            log_msg(self.serial, f"訪客登入嘗試第 {attempt} 次")

            if 3 <= attempt:
                force_close(self.serial)
                open_game(self.serial)

            connection_retry(self.serial, retry=Confirm.SMALL, wait_name=GameView.WAITING)
            if exist_click(self.serial, GameView.GUEST_LOGIN, threshold=0.5):
                return True

            if not wait(self.serial, GameView.LOGIN_LINE, timeout=10.0):
                raise GameError("找不到 Login with Line，遊戲崩潰")

            wait_click(self.serial, GameView.LOGIN_LINE)
            self._agree_terms()

            if not force_close_line(self.serial, timeout=3.0):
                for _ in range(3):
                    back(self.serial)

            wait_click(self.serial, GameView.ICON, threshold=0.5)
            if wait_click(self.serial, GameView.GUEST_LOGIN, threshold=0.5):
                log_msg(self.serial, "訪客登入成功")
                return True
            else:
                log_msg(self.serial, "找不到訪客登入，重試")
        
        raise GameError("多次嘗試訪客登入仍失敗")

    def _on_loading_page(self, timeout: float = 900.0):
        start = time.time()

        while time.time() - start < timeout:
            if wait(self.serial, GameView.LOADING, timeout=3.0):
                if exist(self.serial, Confirm.SMALL):
                    if not exist(self.serial, GameView.DOWNLOAD_TEXT):
                        wait_click(self.serial, Confirm.SMALL)
                        wait_click(self.serial, GameView.PLAY_BTN, timeout=25.0)
                        start = time.time()
                        continue 
                    else:
                        wait_click(self.serial, Confirm.SMALL)
                elif exist(self.serial, Retry.TEXT1):
                    wait_click(self.serial, Retry.BTN, wait_time=1.0)
                    start = time.time()
                    continue
            else:
                if exist(self.serial, GameView.ICON):
                    return False
                else:
                    return True

            time.sleep(1.0)
        raise GameError("正在 login, 但未知狀態")

    def _guest_login(self, mode: str = None):
        open_game(self.serial, mode)

        for _ in range(10):
            in_game = False

            if wait(self.serial, GameView.WAITING, timeout=3.0):
                in_game = True
                if exist(self.serial, GameView.AUTH_FAILED):
                    wait_click(self.serial, Confirm.SMALL)

                if exist(self.serial, Retry.TEXT1):
                    wait_click(self.serial, Confirm.SMALL, wait_time=2.0)
                    wait_click(self.serial, GameView.PLAY_BTN, timeout=3.0)

                timeout_count = 5.0
                if wait(self.serial, GameView.LOGIN_LINE):
                    timeout_count = 25.0
                    self._trigger_guest_btn()
                    if wait_click(self.serial, GameView.GUEST_CONNECT, threshold=0.5):
                        self._agree_terms()

                if wait(self.serial, Confirm.SMALL, timeout=timeout_count):
                    in_game = True
                    if exist(self.serial, GameView.ENG_BTN):
                        exist_click(self.serial, Confirm.SMALL)
                    elif exist(self.serial, Confirm.CANCEL):
                        exist_click(self.serial, Confirm.SMALL)

            if wait(self.serial, GameView.LOADING, timeout=3.0):
                in_game = True
                if self._on_loading_page():
                    return
                
            if in_game == False:
                return # 已經在遊戲內了
        raise GameError("無法訪客登入")
                
    def general_guest_login(self, mode: str = "main_stage"):
        if mode == "":
            self._guest_login()
        else:
            self._guest_login(mode=mode)

def first_guest_login(serial):
    login_flow = BaseLoginFlow(serial)
    login_flow.general_guest_login(mode="pre_stage")
            
def guest_login(serial, mode: str = "main_stage"):
    login_flow = BaseLoginFlow(serial)
    login_flow.general_guest_login(mode=mode)