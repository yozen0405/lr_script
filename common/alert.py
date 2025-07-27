import time
import os
from logger import log_msg
from action import wait_click, exist_click, exist, wait, wait_vanish, extract_text, back, drag, force_close
from exceptions import GameError

import time

def connection_retry(
    serial,
    image_name=None,
    wait_name=None,
    retry="retry.png",
    retry_text="retry_text.png",
    exception_msg="等待畫面失敗",
    timeout=15.0
):
    start_time = time.time()
    while time.time() - start_time < timeout:
        if image_name and not exist(serial, image_name):
            return True
        if wait_name and exist(serial, wait_name):
            return True
        if wait(serial, retry_text, timeout=1.5):
            wait_click(serial, retry, wait_time=4.0)
        time.sleep(0.5)

    raise GameError(exception_msg)
    

def liapp_alert(serial, esc=True):
    if wait(serial, "liapp_icon.png", timeout=10.0):
        wait_click(serial, "liapp_confirm.png")
    if esc and wait(serial, "gameicon.png", timeout=5.0):
        raise GameError("出現liapp alert, 強制退出")
    

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