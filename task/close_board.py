import time
import os
from adb_runner import adb_cmd
from logger import log_msg
from action import wait_click, exist_click, exist, wait, wait_vanish, extract_text, back, drag
from location.pair import positions
from exceptions import GameError

def close_board(serial, attempts=15):
    num = 0
    for _ in range(attempts):
        if wait_click(serial, "close_board.png"):
            num = 0
            continue
        elif wait_click(serial, "confirm_small.png"):
            num = 0
            continue
        else:
            num += 1
            if num == 2:
                break
