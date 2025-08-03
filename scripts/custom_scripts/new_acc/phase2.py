import time
import os
from core.system.logger import log_msg
from core.actions.actions import wait_click, exist_click, exist, wait, wait_vanish, extract_text, back, drag, force_close
from core.base.exceptions import GameError
from scripts.shared.utils.game_view import close_board
from scripts.shared.events.main_stage import MainStageTask
from scripts.shared.utils.retry import connection_retry
from scripts.shared.utils.game_boot import open_game_with_hacks
from scripts.shared.utils.game_view import on_main_view
from scripts.shared.events.login import login_entry

main_stage_task = None

class SecondStageTask(MainStageTask):
    def settlement(self):
        wait(self.serial, "main_stage_settlement_text.png", timeout=25.0)
        for _ in range(3):
            wait_click(self.serial, self.MEMBER4_POS, wait_time=1.5)
        for _ in range(10):
            exist_click(self.serial, "acquired.png")
            exist_click(self.serial, "confirm_big.png")
            if exist_click(self.serial, "skip.png"):
                wait_click(self.serial, "confirm_small.png", wait_time=0.5)
            if exist_click(self.serial, "stop.png"):
                break

class ThirdStageTask(MainStageTask):
    def teach(self):
        time.sleep(1.0)
        if not wait_click(self.serial, "speed_up_btn_off.png", wait_time=3.0):
            raise GameError("無法點擊x2")
        if not wait_click(self.serial, "speed_up_btn_on.png"):
            raise GameError("無法點擊x2")
        if not wait_click(self.serial, "speed_up_btn_on.png"):
            raise GameError("無法點擊x2")

def login_second(serial):
    log_msg(serial, "二次登入")

    login_entry(serial)
    wait_click(serial, "confirm_small.png", timeout=60.0)
    connection_retry(serial, "loading_page.png", timeout=900.0)
    if exist(serial, "gameicon.png"):
        login_entry(serial, hacks=True)
        wait_click(serial, "confirm_small.png", timeout=40.0)
        connection_retry(serial, "loading_page.png", timeout=900.0)
        if exist(serial, "gameicon.png"):
            raise GameError("遊戲崩潰, 強制停止")
        
    if not wait_vanish(serial, "loading_page.png", timeout=2.0):
        raise GameError("無法進入遊戲")

    close_board(serial)

def second_stage(serial):
    log_msg(serial, "打主要關卡stage2")
    wait_click(serial, "skip.png", timeout=3.0)
    second_stage_task = SecondStageTask(serial)
    second_stage_task.enter_menu()
    second_stage_task.enter_stage()
    second_stage_task.run(anime=False, has_next=False, big_ok=True)

def claim_treasure(serial, main_stage_task):
    log_msg(serial, "尋找寶物")
    on_main_view(serial, sign="back.png", vanish=True)
    if wait_click(serial, "skip.png", timeout=20.0):
        wait_click(serial, "confirm_small.png", wait_time=0.5)
    main_stage_task.enter_menu()
    if not wait_click(serial, "treasure_icon.png", timeout=40.0):
        raise GameError("無法進入寶物")

    if not wait(serial, "treasure_text.png", timeout=30.0):
        raise GameError("不在寶物室，強制停止")
    if wait_click(serial, "skip.png", timeout=20.0):
        wait_click(serial, "confirm_small.png", wait_time=0.5)

    if wait_click(serial, "back.png", timeout=20.0):
        wait_click(serial, "confirm_small.png", wait_time=0.5)

    third_stage_task = ThirdStageTask(serial)
    third_stage_task.enter_stage()
    third_stage_task.run(anime=False, has_next=False, big_ok=True)
    wait_click(serial, "back.png", timeout=10.0)
    on_main_view(serial, sign="back.png", vanish=True)

    if wait_click(serial, "skip.png", timeout=5):
        wait_click(serial, "confirm_small.png", wait_time=0.5)

    wait_click(serial, "long_quest.png", timeout=7.0)
    wait_click(serial, "close_board.png", timeout=10.0)

def seven_days(serial, main_stage_task):
    wait_click(serial, "back.png")
    on_main_view(serial, sign="back.png", vanish=True)

    if wait_click(serial, "skip.png", timeout=5):
        wait_click(serial, "confirm_small.png", wait_time=0.5)
    
    wait_click(serial, "7days.png", timeout=7.0)
    if wait_click(serial, "skip.png", timeout=10):
        wait_click(serial, "confirm_small.png", wait_time=0.5)
    wait_click(serial, "7days_info.png", timeout=7.0)
    wait_click(serial, "close_board.png", timeout=10.0, wait_time=1.0)
    wait_click(serial, "close_board.png", timeout=10.0)
    
def normal_stage(serial, main_stage_task, enter_menu=False):
    if enter_menu:
        main_stage_task.enter_menu()
    main_stage_task.enter_stage()
    main_stage_task.run(anime=False, has_next=False, big_ok=True)

def upgrade_sheep(serial, main_stage_task):
    on_main_view(serial, sign="back.png", vanish=True)

    if wait_click(serial, "skip.png", timeout=5.0):
        wait_click(serial, "confirm_small.png", wait_time=3.0)

    wait_click(serial, "sheep.png", timeout=7.0, wait_time=2.0)
    wait_click(serial, "upgrade_btn.png")
    if not wait(serial, "back.png", timeout=20.0):
        raise GameError("無法進入升級頁面")
    drag(serial, (80, 574), (478, 341), wait_time=3.0, timeout=10.0)
    wait_click(serial, "upgrade_lvl_btn.png")
    for _ in range(3):
        wait_click(serial, "upgrade_success.png", timeout=5.0, wait_time=1.0)
    if wait_click(serial, "skip.png", timeout=15.0):
        wait_click(serial, "confirm_small.png")
    wait_click(serial, "back.png")

def back_to_close_board(serial):
    if not wait(serial, "main_stage_text.png", timeout=15.0):
        raise GameError("不在主畫面")
    wait_click(serial, "back.png")
    on_main_view(serial, sign="back.png", vanish=True)
    force_close(serial)

def phase2(serial):
    main_stage_task = MainStageTask(serial)

    try:
        login_second(serial)
    except GameError as e:
        raise
    try:
        second_stage(serial)
    except GameError as e:
        raise
    try:
        claim_treasure(serial, main_stage_task)
    except GameError as e:
        raise
    try:
        normal_stage(serial, main_stage_task, enter_menu=True)
    except GameError as e:
        raise
    
    try:
        seven_days(serial, main_stage_task)
    except GameError as e:
        raise
    try:
        normal_stage(serial, main_stage_task, enter_menu=True)
    except GameError as e:
        raise
    try:
        upgrade_sheep(serial, main_stage_task)
    except GameError as e:
        raise
    try:
        normal_stage(serial, main_stage_task, enter_menu=True)
    except GameError as e:
        raise
    try:
        back_to_close_board(serial)
    except GameError as e:
        raise
