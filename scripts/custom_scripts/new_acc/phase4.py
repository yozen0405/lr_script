import time
import os
from core.system.logger import log_msg
from core.actions.actions import wait_click, exist_click, exist, wait, wait_vanish, back, drag, force_close
from core.base.exceptions import GameError
from scripts.shared.utils.game_view import close_board
from scripts.shared.events.special_stage.selector import special_stage_single_game
from scripts.shared.utils.retry import connection_retry
from scripts.shared.utils.game_view import on_main_view
from scripts.shared.events.main_stage.selector import main_stage_finish_new, main_stage_enter_menu

def upgrade_equip(serial):
    log_msg(serial, "升級裝備")
    on_main_view(serial)

    if wait_click(serial, "skip.png", timeout=5.0):
        wait_click(serial, "confirm_small.png", wait_time=3.0)

    wait_click(serial, "rene.png", timeout=7.0, wait_time=2.0)
    wait_click(serial, "rene_go_equip.png", timeout=10.0)

    connection_retry(serial, wait_name="equip_text.png", exception_msg="沒進去裝備頁面", timeout=40.0)

    wait_click(serial, "skip.png", timeout=5.0, wait_time=1.2)
    wait_click(serial, "equip_shield_icon.png", timeout=5.0, wait_time=1.2)
    if wait_click(serial, "skip.png", timeout=5.0):
        wait_click(serial, "confirm_small.png", wait_time=3.0)
    wait_click(serial, "equip_go_upgrade.png", timeout=5.0, wait_time=2.0, threshold=0.99)
    if wait_click(serial, "skip.png", timeout=5.0):
        wait_click(serial, "confirm_small.png", wait_time=3.0)
    wait_click(serial, "equip_shield_icon.png", timeout=5.0, wait_time=2.0)
    wait_click(serial, "equip_upgrade.png", timeout=5.0, wait_time=3.0)
    for _ in range(3):
        if not wait_click(serial, "equip_upgrade_finish.png", timeout=5.0, wait_time=1.5):
            break
    if wait_click(serial, "skip.png", timeout=5.0):
        wait_click(serial, "confirm_small.png", wait_time=3.0)
    wait_click(serial, "back.png")

def introduce_scene(serial):
    wait_click(serial, "back.png")
    on_main_view(serial, sign="gacha_skip.png", vanish=False, timeout=40.0)

    wait_click(serial, "gacha_skip.png", timeout=5.0, wait_time=2.0)
    special_stage_single_game(serial, planet="evo_mine.png", stage=1)
    wait_click(serial, "back.png", wait_time=2.0)
    

def phase4(serial):
    log_msg(serial, "第四階段")

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
        upgrade_equip(serial)
    except GameError as e:
        raise

    try:
        main_stage_finish_new(serial)
    except GameError as e:
        raise

    for _ in range(9):
        try:
            main_stage_finish_new(serial)
        except GameError as e:
            raise

    try:
        introduce_scene(serial)
    except GameError as e:
        raise