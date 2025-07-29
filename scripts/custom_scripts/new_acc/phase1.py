import time
import os
from core.system.adb import adb_cmd
from core.system.logger import log_msg
from scripts.shared.events.login import first_time_login
from core.actions.actions import wait_click, exist_click, exist, wait, wait_vanish, extract_text, back, drag
from scripts.shared.utils.retry import connection_retry
from scripts.shared.utils.hacks import apply_mode
from scripts.shared.constants import positions
from core.base.exceptions import GameError
from scripts.shared.events.main_stage import MainStageTask

class FirstStageTask(MainStageTask):
    def pre_select(self):
        wait_click(self.serial, "meteor.png", threshold=0.5)

def pre_stage(serial):
    log_msg(serial, "進去前置關卡")
    connection_retry(serial, retry="retry.png", wait_name="nickname_setup.png", timeout=400)

    if not wait(serial, "nickname_setup.png", threshold=0.5, timeout=20):
        raise GameLoginError("⚠️ 非新手教學")
    
    wait_click(serial, "confirm_small.png")
    wait_click(serial, "confirm_small.png")
    wait_click(serial, "confirm_small.png")

    wait_click(serial, "skip.png")
    wait_click(serial, "confirm_small.png", wait_time=0.5)

    if wait(serial, "pause.png", threshold=0.5, timeout=15.0):
        for _ in range(50):
            if exist_click(serial, "skip.png", threshold=0.8):
                break
            wait_click(serial, positions["member1"], wait_time=0)
            wait_click(serial, positions["member2"], wait_time=0)
            wait_click(serial, positions["member3"], wait_time=0)
            wait_click(serial, positions["member4"], wait_time=0)
            wait_click(serial, positions["member5"], wait_time=0)
            wait_click(serial, positions["diamond"], wait_time=0)
            wait_click(serial, positions["missile"], wait_time=0)
    else:
        raise GameError("無法確認戰鬥狀態，跳出")
    
    wait_click(serial, "confirm_small.png", wait_time=3)

    for _ in range(30):
        if not exist(serial, "pause.png", threshold=0.8):
            break
        wait_click(serial, positions["member1"], wait_time=0)
        wait_click(serial, positions["member2"], wait_time=0)
        wait_click(serial, positions["member3"], wait_time=0)
        wait_click(serial, positions["member4"], wait_time=0)
        wait_click(serial, positions["member5"], wait_time=0)
        wait_click(serial, positions["missile"], wait_time=0)
    
    if wait_click(serial, "skip.png", timeout=5.0):
        wait_click(serial, "confirm_small.png", wait_time=2)

    if wait_click(serial, "skip.png", timeout=5.0):
        wait_click(serial, "confirm_small.png", wait_time=2)

def first_stage(serial):
    log_msg(serial, "遊戲開場介紹")
    if not wait(serial, "settings_btn.png", timeout=40.0):
        raise GameError("不在主畫面")

    if wait_click(serial, "skip.png", timeout=5.0):
        wait_click(serial, "confirm_small.png", wait_time=2)
    
    wait_click(serial, "skip.png", timeout=5.0)

    first_stage_task = FirstStageTask(serial)
    first_stage_task.enter_menu()
    apply_mode(serial, "main_stage", True, True)
    first_stage_task.enter_stage()
    first_stage_task.run(anime=True, bonus=False, has_next=False)

def first_ranger(serial):
    if not wait(serial, "gacha_icon.png", timeout=20.0, threshold=0.97):
        raise GameError("不再主畫面")
    wait_click(serial, "skip.png")
    wait_click(serial, "confirm_small.png")
    wait_click(serial, "gacha_icon.png", timeout=7.0)
    if not wait(serial, "gacha_text.png", timeout=20.0):
        raise GameError("無法進入扭蛋")
    wait_click(serial, "skip.png", timeout=1.5)
    wait_click(serial, "gacha_jessica.png")
    wait_click(serial, "gacha_skip.png")
    wait_click(serial, "confirm_small.png")
    wait_click(serial, "gacha_confirm.png")
    wait_click(serial, "skip.png")
    wait_click(serial, "confirm_small.png")


def first_arrange_team(serial):
    connection_retry(serial, wait_name="settings_btn.png", timeout=35.0)
    if wait_click(serial, "skip.png", timeout=3):
        wait_click(serial, "confirm_small.png", wait_time=0.5)
    wait_click(serial, "team_icon.png")
    if not wait_click(serial, "leonard_teacher.png", timeout=20):
        raise GameError("找不到隊伍教學")
    wait_click(serial, "leonard_teacher.png")

    if exist(serial, "leonard_teacher.png"):
        drag(serial, "cony_for_drag.png", "jessica_drag_end.png", wait_time=1.0, timeout=10.0)
        drag(serial, "jessica_drag_end.png", "drag_end_for_jessica.png", wait_time=1.0, timeout=10.0)

    wait_click(serial, "skip.png")
    wait_click(serial, "confirm_small.png")
    wait_click(serial, "save_team.png", wait_time=3.0)
    connection_retry(serial, wait_name="settings_btn.png", exception_msg="未進入主畫面，隊伍教學失敗", timeout=35.0)
    for _ in range(3):
        if wait_click(serial, "skip.png", timeout=5, wait_time=1.0):
            if not exist(serial, "confirm_small.png"):
                continue
            wait_click(serial, "confirm_small.png", wait_time=0.5)
            break
    wait_click(serial, "confirm_small.png", wait_time=0.5)

def phase1(serial):
    try:
        first_time_login(serial)
    except GameError as e:
        raise

    try:
        pre_stage(serial)
    except GameError as e:
        raise

    try:
        first_stage(serial)
    except GameError as e:
        raise

    try:
        first_ranger(serial)
    except GameError as e:
        raise

    try:
        first_arrange_team(serial)
    except GameError as e:
        raise
    