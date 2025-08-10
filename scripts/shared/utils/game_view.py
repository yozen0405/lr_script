import time
import os
from core.system.logger import log_msg
from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, back, drag
from core.base.exceptions import GameError

def on_main_view(serial, sign="back.png", vanish=True, skip_included = False, timeout=25.0):
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
        
        if exist(serial, "settings_btn.png", wait_time=3.0):
            found = True
            break
        if exist_click(serial, "confirm_small.png", wait_time=1.0):
            found = True
            break
        if exist_click(serial, "close_board.png", wait_time=3.0):
            found = True
            break
        if exist_click(serial, "close_to_pvp.png", wait_time=1.0):
            found = True
            break
        if exist_click(serial, "cancel.png", wait_time=3.0):
            found = True
            break
        time.sleep(0.5)

    close_board(serial)
    if skip_included:
        for _ in range(5):
            if wait_click(serial, "skip.png", timeout=3.0, wait_time=1.0):
                wait_click(serial, "confirm_small.png", timeout=1.5)
            else:
                break

    if exist_click(serial, "close_board.png", wait_time=3.0):
        found = True
    if exist_click(serial, "close_to_pvp.png", wait_time=1.0):
        found = True
    if exist_click(serial, "cancel.png", wait_time=3.0):
        found = True

    if not found:
        raise GameError("沒有進入到主畫面")
    
def close_board(serial, attempts=25):
    num = 0
    for _ in range(attempts):
        if wait_click(serial, "board_dont_show.png", timeout=3.0):
            wait_click(serial, "close_board.png", timeout=3.0)
            num = 0
            continue
        if wait_click(serial, "close_board.png", timeout=3.0):
            num = 0
            continue
        elif wait(serial, "board_end2.png", timeout=3.0, threshold=0.9):
            wait_click(serial, "confirm_small.png", wait_time=2.5)
            num = 0
            continue
        else:
            num += 1
            if num == 1:
                break


def reliable_click(
    serial,
    target_img,
    confirm_img=None,
    max_retry=3,
    wait_time=1.0,
    check_disappear=True
):
    """
    :param serial: 裝置序號
    :param target_img: 要點擊的主要圖片
    :param confirm_img: 若出現確認視窗，要點擊的圖片（可省略）
    :param max_retry: 點擊主圖最多嘗試幾次
    :param wait_time: 每次點擊後的等待秒數
    :param check_disappear: 點擊後是否確認圖片消失
    """
    for attempt in range(max_retry):
        if wait_click(serial, target_img, wait_time=wait_time):
            if check_disappear and exist(serial, target_img):
                continue

            if confirm_img and exist(serial, confirm_img):
                wait_click(serial, confirm_img, wait_time=wait_time)
            return
    raise GameError(f"點擊 {target_img} 失敗")