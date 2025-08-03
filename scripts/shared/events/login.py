import time
from core.system.logger import log_msg
from core.actions.actions import wait_click, exist_click, exist, wait, wait_vanish, extract_text, back, drag, force_close
from core.base.exceptions import GameError
from scripts.shared.utils.retry import connection_retry
from scripts.shared.utils.game_boot import open_game, open_game_with_hacks

def attempt_guest_login(serial):
    for attempt in range(1, 3):
        log_msg(serial, f"訪客登入嘗試第 {attempt} 次")

        connection_retry(serial, retry="confirm_small.png", wait_name="game_waiting_page.png")

        if exist_click(serial, "guest_login.png", threshold=0.5):
            return True

        if not wait(serial, "login_line.png", timeout=10.0):
            raise GameError("⚠️ 找不到 Login with Line，遊戲可能崩潰")

        wait_click(serial, "login_line.png")
        wait(serial, "line_game_text.png", threshold=0.5, timeout=15.0)

        for _ in range(15):
            if exist(serial, "terms_complete.png", threshold=0.99):
                break
            exist_click(serial, "terms.png", threshold=0.5)

        if not exist(serial, "terms_complete.png", threshold=0.99):
            raise GameError("條款認證失敗")

        wait_click(serial, "agreeTerms.png", threshold=0.5)

        for _ in range(3):
            back(serial)

        wait_click(serial, "gameicon.png", threshold=0.5)
        if wait_click(serial, "guest_login.png", threshold=0.5):
            log_msg(serial, "訪客登入成功")
            return True
        else:
            log_msg(serial, "找不到訪客登入，重試")
    
    raise GameError("多次嘗試訪客登入仍失敗")

def finalize_guest_login(serial):
    if not wait_click(serial, "game_waiting_page.png", timeout=10.0, threshold=0.5):
        raise GameError("無法進行訪客登入")

    attempt_guest_login(serial)
    wait_click(serial, "guest_connect.png", threshold=0.5)

    for _ in range(15):
        if exist(serial, "terms_complete.png", threshold=0.99):
            break
        exist_click(serial, "terms.png", threshold=0.5)

    if not exist(serial, "terms_complete.png", threshold=0.99):
        raise GameError("協議認證失敗")

    wait_click(serial, "agreeTerms.png", threshold=0.5)

def _wait_loading_page(serial, hacks, load_in, close):
    if load_in:
        if wait_vanish(serial, "loading_page.png", timeout=300.0):
            if exist(serial, "gameicon.png"):
                if close:
                    raise GameError("無法進入遊戲主畫面")
                login_entry(serial, hacks, load_in, close=True)
            

def login_entry(serial, hacks=False, load_in=False, close=False):
    if wait(serial, "gameicon.png"):
        if hacks:
            open_game_with_hacks(serial, "main_stage")
        else:
            open_game(serial)

    if not wait(serial, "loading_page.png", timeout=30.0):
        if exist(serial, "game_waiting_page.png", threshold=0.5):
            if exist(serial, "auth_failed.png"):
                wait_click(serial, "confirm_small.png")
                finalize_guest_login(serial)
                _wait_loading_page(serial, hacks, load_in, close)
    else:
        _wait_loading_page(serial, hacks, load_in, close)
        return

