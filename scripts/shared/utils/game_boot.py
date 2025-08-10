import time
import os
from core.system.logger import log_msg
from core.actions.actions import wait_click, exist_click, exist, wait, wait_vanish, back, drag, force_close
from core.base.exceptions import GameError
from scripts.shared.utils.hacks import apply_mode

def open_game(serial):
    if not wait_click(serial, "gameicon.png", threshold=0.5):
        raise GameError("不在桌面")
    wait(serial, "open_game.png", threshold=0.5, timeout=15.0)
    
    for i in range(3):
        if wait_vanish(serial, "open_game.png", threshold=0.5, timeout=15.0):
            wait_click(serial, "confirm_perm.png", threshold=0.5, timeout=7.0)
            return True

        log_msg(serial, f"第 {i+1} 次：遊戲卡在開啟畫面，嘗試重新啟動...")
        force_close(serial)

        if not wait_click(serial, "gameicon.png", threshold=0.5, timeout=15.0):
            raise GameError("無法點擊遊戲圖示")

        if wait(serial, "open_game.png", threshold=0.5, timeout=15.0):
            continue
    raise GameError("遊戲啟動卡住多次，重啟無效")

def open_game_with_hacks(serial, mode: str = "main_stage"):
    for attempt in range(1, 3):
        open_game(serial)
        apply_mode(serial, mode_name=mode, state="on")
        time.sleep(3)

        if wait(serial, "loading_page.png", threshold=0.5, timeout=5.0):
            return

        if wait(serial, "game_waiting_page.png", threshold=0.5, timeout=5.0):
            return

        if wait_click(serial, "gameicon.png", threshold=0.5, timeout=5.0):
            continue

    raise GameError(f"嘗試 3 次後仍無法啟動遊戲")
