import time
import os
from core.system.logger import log_msg
from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, back, drag
from core.base.exceptions import GameError
from scripts.shared.constants import MainView, Confirm

def on_main_view(serial, sign=MainView.BACK, vanish=True, skip_included = False, timeout=25.0):
    start_time = time.time()
    found = False

    while time.time() - start_time < timeout:
        if vanish:
            if exist(serial, sign):
                if wait_vanish(serial, sign, wait_time=3.0):
                    found = True
                    break
        else:
            if exist(serial, sign, wait_time=3.0):
                found = True
                break
        
        if exist(serial, MainView.SETTINGS, wait_time=3.0):
            found = True
            break
        if exist_click(serial, Confirm.SMALL, wait_time=1.0):
            found = True
            break
        if exist_click(serial, MainView.CLOSE_BOARD, wait_time=3.0):
            found = True
            break
        if exist_click(serial, MainView.CLOSE_PVP, wait_time=1.0):
            found = True
            break
        if exist_click(serial, Confirm.CANCEL, wait_time=3.0):
            found = True
            break
        time.sleep(0.5)

    close_board(serial)
    if skip_included:
        for _ in range(5):
            if wait_click(serial, MainView.SKIP, timeout=3.0, wait_time=1.0):
                wait_click(serial, Confirm.SMALL, timeout=1.5)
            else:
                break

    if exist_click(serial, MainView.CLOSE_BOARD, wait_time=3.0):
        found = True
    if exist_click(serial, MainView.CLOSE_PVP, wait_time=1.0):
        found = True
    if exist_click(serial, Confirm.CANCEL, wait_time=3.0):
        found = True

    if not found:
        raise GameError("沒有進入到主畫面")
    
def close_board(serial, attempts=25):
    num = 0
    for _ in range(attempts):
        if wait_click(serial, MainView.BOARD_DONT_SHOW, timeout=3.0):
            wait_click(serial, MainView.CLOSE_BOARD, timeout=3.0)
            num = 0
            continue
        if wait_click(serial, MainView.CLOSE_BOARD, timeout=3.0):
            num = 0
            continue
        elif wait(serial, MainView.BOARD_END, timeout=3.0, threshold=0.9):
            wait_click(serial, Confirm.SMALL, wait_time=2.5)
            num = 0
            continue
        else:
            num += 1
            if num == 1:
                break