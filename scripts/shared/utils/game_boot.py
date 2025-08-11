import time
from core.system.logger import log_msg
from core.actions.screen import (
    wait_click, exist_click, exist, wait, wait_vanish, back, drag
)
from core.actions.system import force_close
from core.base.exceptions import GameError
from scripts.shared.utils.hacks import apply_mode
from scripts.shared.constants import MainView, Confirm, GameView

def open_game(serial, mode: str = "main_stage"):
    succ = False
    on_open = 0
    while True:
        if exist_click(serial, GameView.ICON, threshold=0.5):
            on_open = 0
            if not wait(serial, GameView.GAME_OPENED, threshold=0.5, timeout=10.0):
                log_msg(serial, "遊戲卡在開啟畫面，嘗試重新啟動...")
                force_close(serial)
                continue

        if exist(serial, GameView.GAME_OPENED):
            on_open = 0
            if not wait_vanish(serial, GameView.GAME_OPENED, threshold=0.5, timeout=15.0):
                log_msg(serial, "遊戲卡在開啟畫面，嘗試重新啟動...")
                force_close(serial)
                continue

        if exist_click(serial, GameView.PERM):
            on_open = 0

        if exist_click(serial, GameView.LINE_STUDIO_TEXT):
            on_open = 0
        
        if exist(serial, GameView.LOADING):
            succ = True
            break
        
        if exist(serial, GameView.WAITING):
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