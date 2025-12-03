import time
import os
from core.system.logger import log_msg
from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, back, drag
from core.base.exceptions import GameError
from scripts.shared.constants import MainView, Confirm, Retry


def on_main_view(serial, sign=MainView.BACK.value, vanish=True, skip_included = False, timeout=25.0):
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

        if exist(serial, Retry.TEXT1.value):
            exist_click(serial, Retry.BTN.value)
        if exist(serial, Confirm.SMALL.value, threshold=0.9):
            if not exist(serial, Retry.TEXT2.value):
                found = True
                exist_click(serial, Confirm.SMALL.value, wait_time=1.0)
                break
            exist_click(serial, Confirm.SMALL.value, wait_time=1.0)
            exist_click(serial, sign)
        
        if exist(serial, MainView.SETTINGS.value, wait_time=3.0):
            found = True
            break
        if exist_click(serial, MainView.CLOSE_BOARD.value, wait_time=3.0):
            found = True
            break
        if exist_click(serial, MainView.CLOSE_PVP.value, wait_time=1.0):
            found = True
            break
        if exist_click(serial, Confirm.CANCEL.value, wait_time=3.0):
            found = True
            break
        if exist_click(serial, MainView.SKIP_2.value, wait_time=1.0):
            found = True
            break
        time.sleep(0.5)

    close_board(serial)
    if skip_included:
        for _ in range(5):
            if wait_click(serial, MainView.SKIP.value, timeout=3.0, wait_time=1.0):
                wait_click(serial, Confirm.SMALL.value, timeout=1.5)
            else:
                break

    if exist_click(serial, MainView.CLOSE_BOARD.value, wait_time=3.0):
        found = True
    if exist_click(serial, MainView.CLOSE_PVP.value, wait_time=1.0):
        found = True
    if exist_click(serial, Confirm.CANCEL.value, wait_time=3.0):
        found = True
    if exist_click(serial, MainView.SKIP_2.value, wait_time=1.0):
        found = True

    if not found:
        raise GameError("沒有進入到主畫面")
    
def close_board(serial):
    num = 0
    start_time = time.time()
    while time.time() - start_time < 600.0:
        if exist_click(serial, MainView.BOARD_DONT_SHOW.value):
            wait_click(serial, MainView.CLOSE_BOARD.value, timeout=3.0)
            num = 0
            continue
        if exist_click(serial, MainView.CLOSE_BOARD.value):
            num = 0
            continue
        elif exist_click(serial, MainView.BOARD_END.value, timeout=3.0, threshold=0.9):
            wait_click(serial, Confirm.SMALL.value, wait_time=1.0)
            num = 0
            continue
        else:
            num += 1
            if num == 1:
                return
    raise GameError("關閉公告版失敗")