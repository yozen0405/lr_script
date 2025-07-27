import time
import os
from logger import log_msg
from action import wait_click, exist_click, exist, wait, wait_vanish, extract_text, back, drag, force_close
from exceptions import GameError

def loop_confirm(serial):
    for _ in range(3):
        if wait_click(serial, "skip.png", timeout=5, wait_time=1.0):
            if not exist(serial, "confirm_small.png"):
                continue
            wait_click(serial, "confirm_small.png", wait_time=0.5)
            break

def loop_click(serial, img):
    for _ in range(3):
        if wait_click(serial, img):
            if exist(serial, img):
                return
    raise GameError("重複點擊失敗")