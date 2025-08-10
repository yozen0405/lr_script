import time
from core.system.logger import log_msg
from core.actions.actions import (
    wait_click, exist_click, exist, wait, wait_vanish, back, drag, force_close
)
from core.base.exceptions import GameError
from scripts.shared.utils.hacks import apply_mode

def open_game(serial, mode: str = "main_stage"):
    succ = False
    on_open = 0
    while True:
        if exist_click(serial, "gameicon.png", threshold=0.5):
            on_open = 0
            if not wait(serial, "open_game.png", threshold=0.5, timeout=10.0):
                log_msg(serial, "遊戲卡在開啟畫面，嘗試重新啟動...")
                force_close(serial)
                continue

        if exist(serial, "open_game.png"):
            on_open = 0
            if not wait_vanish(serial, "open_game.png", threshold=0.5, timeout=15.0):
                log_msg(serial, "遊戲卡在開啟畫面，嘗試重新啟動...")
                force_close(serial)
                continue

        if exist_click(serial, "confirm_perm.png"):
            on_open = 0

        if exist_click(serial, "open_game_line_studio_text.png"):
            on_open = 0
        
        if exist(serial, "loading_page.png"):
            succ = True
            break
        
        if exist(serial, "game_waiting_page.png"):
            succ = True
            break
        
        on_open += 1
        if on_open >= 2:
            succ = True
            break
    
    if succ:
        apply_mode(serial, mode_name=mode, state="on")
    else:
        raise GameError("遊戲啟動卡住多次，重啟無效")