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

def claim_board(serial):
    log_msg(serial, "第三階段")
    login_entry(serial, hacks=True, load_in=True)
    close_board(serial)

def normal_stage(serial, main_stage_task, enter_menu=False):
    if enter_menu:
        main_stage_task.enter_menu()
    main_stage_task.enter_stage()
    main_stage_task.run(anime=False, has_next=False, big_ok=True)

def upgrade_rene(serial):
    log_msg(serial, "升級炳妮")
    on_main_view(serial)

    if wait_click(serial, "skip.png", timeout=5.0):
        wait_click(serial, "confirm_small.png", wait_time=3.0)

    wait_click(serial, "rene.png", timeout=7.0, wait_time=2.0)
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

def gacha_equip(serial, main_stage_task):
    on_main_view(serial)

    if wait_click(serial, "skip.png", timeout=20.0):
        wait_click(serial, "confirm_small.png", wait_time=3.0)
    
    if not wait(serial, "gacha_icon.png", timeout=20.0, threshold=0.97):
        raise GameError("不再主畫面")
    wait_click(serial, "gacha_icon.png", timeout=7.0)
    if not wait(serial, "gacha_text.png", timeout=20.0):
        raise GameError("無法進入扭蛋")
    
    if wait_click(serial, "skip.png", timeout=5.0):
        wait_click(serial, "confirm_small.png", wait_time=3.0)
    wait_click(serial, "gacha_equip_nav.png")
    wait_click(serial, "gacha_equip_pull.png")
    wait_click(serial, "gacha_skip.png")
    if not wait_click(serial, "gacha_confirm.png"):
        raise GameError("無法進行扭蛋")
    if not wait_click(serial, "back.png"):
        raise GameError("找不到返回鍵")
    if wait_click(serial, "skip.png", timeout=20.0):
        wait_click(serial, "confirm_small.png", wait_time=3.0)
    wait_click(serial, "rene.png", timeout=7.0, wait_time=4.0)
    if wait_click(serial, "skip.png", timeout=10.0):
        wait_click(serial, "confirm_small.png", wait_time=1.0)
    wait_click(serial, "skip.png", timeout=10.0, wait_time=2.0)
    wait_click(serial, "rene_go_equip.png", timeout=10.0)

    if not wait(serial, "equip_text.png", timeout=20.0):
        raise GameError("沒進去裝備頁面")
    if wait_click(serial, "skip.png", timeout=5.0):
        wait_click(serial, "confirm_small.png", wait_time=3.0)
    wait_click(serial, "leonard_teacher_equip.png", wait_time=3)
    wait_click(serial, "leonard_teacher_equip.png", wait_time=3)
    wait_click(serial, "leonard_teacher_equip2.png", wait_time=1.5)
    wait_click(serial, "equip_shirt.png", wait_time=2)
    wait_click(serial, "go_equip_shirt.png", wait_time=1.5)
    wait_click(serial, "skip.png", timeout=15.0, wait_time=1.5)
    wait_click(serial, "skip.png", timeout=3.0, wait_time=3.0)
    wait_click(serial, "back.png")

    on_main_view(serial)
    main_stage_task.enter_menu()
    wait_click(serial, "back.png")
    

def phase3(serial):
    main_stage_task = MainStageTask(serial)
    try:
        claim_board(serial)
    except GameError as e:
        raise

    try:
        normal_stage(serial, main_stage_task, enter_menu=True)
    except GameError as e:
        raise

    try:
        normal_stage(serial, main_stage_task, enter_menu=False)
    except GameError as e:
        raise

    try:
        normal_stage(serial, main_stage_task, enter_menu=False)
    except GameError as e:
        raise

    try:
        normal_stage(serial, main_stage_task, enter_menu=False)
    except GameError as e:
        raise

    try:
        upgrade_rene(serial)
    except GameError as e:
        raise

    try:
        normal_stage(serial, main_stage_task, enter_menu=True)
    except GameError as e:
        raise

    try:
        normal_stage(serial, main_stage_task, enter_menu=False)
    except GameError as e:
        raise

    try:
        gacha_equip(serial, main_stage_task)
    except GameError as e:
        raise
