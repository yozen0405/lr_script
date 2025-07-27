import time
import os
from adb_runner import adb_cmd
from logger import log_msg
from action import wait_click, exist_click, exist, wait, wait_vanish, extract_text, back, force_close, launch_game
from exceptions import GameError
from common.alert import connection_retry
from common.alert import open_game
from common.utils import open_game_with_hacks

def trigger_guest_login(serial):
    for attempt in range(1, 3):
        log_msg(serial, f"登入流程嘗試第 {attempt} 次")

        connection_retry(serial, retry="confirm_small.png", wait_name="game_waiting_page.png")
        if exist_click(serial, "guest_login.png", threshold=0.5):
            return
        
        if not wait(serial, "login_line.png", timeout=10.0):
            raise GameError("⚠️ 找不到 login with line, 遊戲崩潰")
        wait_click(serial, "login_line.png")
        wait(serial, "line_game_text.png", threshold=0.5, timeout=15.0)

        for _ in range(15):
            if exist(serial, "terms_complete.png", threshold=1):
                break
            exist_click(serial, "terms.png", threshold=0.5)
        if not exist(serial, "terms_complete.png", threshold=1):
            log_msg(serial, "條款認證失敗")
            continue
        wait_click(serial, "agreeTerms.png", threshold=0.5)

        for _ in range(3):
            back(serial)
        wait_click(serial, "gameicon.png", threshold=0.5) 
        if wait_click(serial, "guest_login.png", threshold=0.5):
            log_msg(serial, "登入流程成功")
            return 
        else:
            log_msg(serial, "找不到訪客登入, 重試")
    
    raise GameError("多次嘗試登入流程仍失敗")

def guest_login(serial):
    if not wait_click(serial, "game_waiting_page.png", timeout=10.0, threshold=0.5):
        raise GameError("無法進行訪客登入")
    trigger_guest_login(serial)
    wait_click(serial, "guest_connect.png", threshold=0.5)
    for _ in range(15):
        if exist(serial, "terms_complete.png", threshold=1):
            break
        exist_click(serial, "terms.png", threshold=0.5)
    if not exist(serial, "terms_complete.png", threshold=1):
        raise GameError("協議認證失敗")
    wait_click(serial, "agreeTerms.png", threshold=0.5)

def ultimate_login(serial, hacks=False, load_in=False):
    if wait(serial, "gameicon.png"):
        if hacks:
            open_game_with_hacks(serial, "main_stage")
        else:
            open_game(serial)

    if not wait(serial, "loading_page.png", timeout=30.0):
        if exist(serial, "game_waiting_page.png"):
            if exist(serial, "auth_failed.png"):
                wait_click(serial, "confirm_small.png")
                guest_login(serial)
                if load_in:
                    if not wait(serial, "settings_btn.png", timeout=300.0):
                        raise GameError("無法進入遊戲主畫面")
    else:
        if load_in:
            if not wait(serial, "settings_btn.png", timeout=300.0):
                raise GameError("無法進入遊戲主畫面")
        return

def login_first(serial):
    log_msg(serial, "首次登入")

    open_game(serial)     
    guest_login(serial)
    connection_retry(serial, retry="confirm_small.png", wait_name="english_btn.png", timeout=35.0)
    
    wait_click(serial, "confirm_small.png", threshold=0.5, timeout=20.0)
