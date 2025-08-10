import time
from core.system.logger import log_msg
from core.actions.actions import wait_click, exist_click, exist, wait, wait_vanish, back, drag, force_close, force_close_line
from core.base.exceptions import GameError
from scripts.shared.utils.retry import connection_retry
from scripts.shared.utils.game_boot import open_game, open_game_with_hacks

class BaseLoginFlow:
    def __init__(self, serial):
        self.serial = serial

    def _agree_terms(self):
        wait(self.serial, "line_game_text.png", threshold=0.5, timeout=30.0)

        for _ in range(15):
            if exist(self.serial, "terms_complete.png", threshold=0.99):
                break
            exist_click(self.serial, "terms.png", threshold=0.5)

        if not exist(self.serial, "terms_complete.png", threshold=0.99):
            raise GameError("條款認證失敗")

        wait_click(self.serial, "agreeTerms.png", threshold=0.5)

    def _trigger_guest_btn(self):
        for attempt in range(1, 5):
            log_msg(self.serial, f"訪客登入嘗試第 {attempt} 次")

            if 3 <= attempt:
                force_close(self.serial)
                open_game(self.serial)

            connection_retry(self.serial, retry="confirm_small.png", wait_name="game_waiting_page.png")
            if exist_click(self.serial, "guest_login.png", threshold=0.5):
                return True

            if not wait(self.serial, "login_line.png", timeout=10.0):
                raise GameError("找不到 Login with Line，遊戲崩潰")

            wait_click(self.serial, "login_line.png")
            self._agree_terms()

            if not force_close_line(self.serial, timeout=3.0):
                for _ in range(3):
                    back(self.serial)

            wait_click(self.serial, "gameicon.png", threshold=0.5)
            if wait_click(self.serial, "guest_login.png", threshold=0.5):
                log_msg(self.serial, "訪客登入成功")
                return True
            else:
                log_msg(self.serial, "找不到訪客登入，重試")
        
        raise GameError("多次嘗試訪客登入仍失敗")

    def _open_game(self, mode):
        log_msg(self.serial, "開啟遊戲中")
        if wait(self.serial, "gameicon.png"):
            if mode:
                open_game_with_hacks(self.serial, mode)
            else:
                open_game(self.serial)

    def _on_loading_page(self, timeout: float = 900.0):
        start = time.time()

        while time.time() - start < timeout:
            if wait(self.serial, "loading_page.png", timeout=3.0):
                if exist(self.serial, "confirm_small.png"):
                    if not exist(self.serial, "loading_page_download.png"):
                        wait_click(self.serial, "confirm_small.png")
                        wait_click(self.serial, "game_waiting_play_btn.png", timeout=25.0)
                        start = time.time()
                        continue 
                    else:
                        wait_click(self.serial, "confirm_small.png")
                elif exist(self.serial, "retry_text.png"):
                    wait_click(self.serial, "retry.png", wait_time=1.0)
                    start = time.time()
                    continue
            else:
                if exist(self.serial, "gameicon.png"):
                    return False
                else:
                    return True

            time.sleep(1.0)
        raise GameError("正在 login, 但未知狀態")

    def _guest_login(self, mode: str = None):
        for _ in range(10):
            if wait(self.serial, "gameicon.png", timeout=3.0):
                self._open_game(mode)

            if wait(self.serial, "game_waiting_page.png", timeout=3.0):
                if exist(self.serial, "auth_failed.png"):
                    wait_click(self.serial, "confirm_small.png")

                if exist(self.serial, "retry_text.png"):
                    wait_click(self.serial, "confirm_small.png", wait_time=2.0)
                    wait_click(self.serial, "game_waiting_play_btn.png", timeout=3.0)

                timeout_count = 5.0
                if wait(self.serial, "login_line.png"):
                    timeout_count = 25.0
                    self._trigger_guest_btn()
                    if wait_click(self.serial, "guest_connect.png", threshold=0.5):
                        self._agree_terms()

                if wait(self.serial, "confirm_small.png", timeout=timeout_count):
                    if exist(self.serial, "english_btn.png"):
                        exist_click(self.serial, "confirm_small.png")
                    else:
                        exist_click(self.serial, "confirm_small.png")

            if wait(self.serial, "loading_page.png", timeout=25.0):
                if self._on_loading_page():
                    return
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