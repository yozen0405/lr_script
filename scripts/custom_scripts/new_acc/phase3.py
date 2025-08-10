import time
import os
from core.system.logger import log_msg
from core.actions.actions import wait_click, exist_click, exist, wait, wait_vanish, back, drag, force_close
from core.base.exceptions import GameError
from scripts.shared.utils.game_view import close_board
from scripts.shared.events.main_stage.selector import main_stage_enter_menu, main_stage_finish_new
from scripts.shared.utils.retry import connection_retry
from scripts.shared.utils.game_view import on_main_view
from scripts.shared.events.login import guest_login

def claim_board(serial):
    log_msg(serial, "第三階段")
    guest_login(serial)
    close_board(serial)

def upgrade_rene(serial):
    log_msg(serial, "升級炳妮")
    on_main_view(serial)

    if wait_click(serial, "skip.png", timeout=5.0):
        wait_click(serial, "confirm_small.png", wait_time=3.0)

    wait_click(serial, "rene.png", timeout=7.0, wait_time=2.0)
    wait_click(serial, "upgrade_btn.png")
    connection_retry(serial, wait_name="back.png", exception_msg="無法進入升級頁面", timeout=40.0)
    drag(serial, (80, 574), (478, 341), wait_time=3.0, timeout=10.0)
    wait_click(serial, "upgrade_lvl_btn.png")
    for _ in range(3):
        wait_click(serial, "upgrade_success.png", timeout=5.0, wait_time=1.0)
    if wait_click(serial, "skip.png", timeout=15.0):
        wait_click(serial, "confirm_small.png")
    wait_click(serial, "back.png")
    connection_retry(serial, image_name="back.png", timeout=40.0)

def gacha_equip(serial):
    on_main_view(serial, "close_board.png", vanish=False)

    if wait_click(serial, "skip.png", timeout=20.0):
        wait_click(serial, "confirm_small.png", wait_time=3.0)
    
    if not wait(serial, "gacha_icon.png", timeout=20.0, threshold=0.97):
        raise GameError("不再主畫面")
    wait_click(serial, "gacha_icon.png", timeout=7.0)
    connection_retry(serial, wait_name="gacha_text.png", timeout=40.0)
    
    if wait_click(serial, "skip.png", timeout=5.0):
        wait_click(serial, "confirm_small.png", wait_time=3.0)
    wait_click(serial, "gacha_equip_nav.png")
    wait_click(serial, "gacha_equip_pull.png")
    wait_click(serial, "gacha_skip.png")
    if not wait_click(serial, "gacha_confirm.png"):
        raise GameError("無法進行扭蛋")
    if not wait_click(serial, "back.png", timeout=20.0):
        raise GameError("找不到返回鍵")
    if wait_click(serial, "skip.png", timeout=30.0):
        wait_click(serial, "confirm_small.png", wait_time=3.0)
    wait_click(serial, "rene.png", timeout=7.0, wait_time=4.0)
    if wait_click(serial, "skip.png", timeout=10.0):
        wait_click(serial, "confirm_small.png", wait_time=1.0)
    wait_click(serial, "skip.png", timeout=10.0, wait_time=2.0)
    wait_click(serial, "rene_go_equip.png", timeout=10.0)

    connection_retry(serial, wait_name="equip_text.png", exception_msg="沒進去裝備頁面", timeout=40.0)
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

    connection_retry(serial, image_name="back.png", timeout=40.0)
    on_main_view(serial)
    main_stage_enter_menu(serial)
    wait_click(serial, "back.png")
    

def phase3(serial):
    try:
        claim_board(serial)
    except GameError as e:
        raise

    try:
        main_stage_finish_new(serial)
    except GameError as e:
        raise

    try:
        main_stage_finish_new(serial)
    except GameError as e:
        raise

    try:
        main_stage_finish_new(serial)
    except GameError as e:
        raise

    try:
        main_stage_finish_new(serial)
    except GameError as e:
        raise

    try:
        upgrade_rene(serial)
    except GameError as e:
        raise

    try:
        main_stage_finish_new(serial)
    except GameError as e:
        raise

    try:
        main_stage_finish_new(serial)
    except GameError as e:
        raise

    try:
        gacha_equip(serial)
    except GameError as e:
        raise
