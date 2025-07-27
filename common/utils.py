import time
import os
from logger import log_msg
from action import wait_click, exist_click, exist, wait, wait_vanish, extract_text, back, drag, force_close
from exceptions import GameError
from hack import apply_mode
from common.alert import connection_retry, open_game

def open_game_with_hacks(serial, mode: str = "main_stage"):
    for attempt in range(1, 3):
        open_game(serial)
        apply_mode(serial, mode, True, False)
        time.sleep(3)

        if wait(serial, "loading_page.png", threshold=0.5, timeout=5.0):
            return

        if wait(serial, "game_waiting_page.png", threshold=0.5, timeout=5.0):
            return

        if wait_click(serial, "gameicon.png", threshold=0.5, timeout=5.0):
            continue

    raise GameError(f"嘗試 3 次後仍無法啟動遊戲")

def on_main_view(serial, sign = "settings_btn.png"):
    if not wait(serial, sign, timeout=25.0, wait_time=4.0):
        raise GameError("沒有進入到主畫面")

    exist_click(serial, "close_board.png", wait_time=3.0)
    exist_click(serial, "close_to_pvp.png", wait_time=1.0)
    exist_click(serial, "cancel.png", wait_time=3.0)


