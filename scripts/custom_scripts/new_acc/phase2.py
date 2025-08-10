from core.system.logger import log_msg
from core.actions.actions import wait_click, exist_click, exist, wait, wait_vanish, back, drag, force_close
from core.base.exceptions import GameError
from scripts.shared.utils.game_view import close_board
from scripts.shared.utils.retry import connection_retry
from scripts.shared.utils.game_view import on_main_view
from scripts.shared.events.login import guest_login
from scripts.shared.events.main_stage.selector import main_stage_finish_new, main_stage_enter_menu

main_stage_task = None

def login_second(serial):
    log_msg(serial, "二次登入")
    guest_login(serial)

    if wait(serial, "settings_btn.png", timeout=40.0):
        close_board(serial)

def second_stage(serial):
    log_msg(serial, "打主要關卡stage2")
    wait_click(serial, "skip.png", timeout=3.0)
    main_stage_finish_new(serial)

def claim_treasure(serial):
    log_msg(serial, "尋找寶物")
    on_main_view(serial, sign="back.png", vanish=True)
    if wait_click(serial, "skip.png", timeout=20.0):
        wait_click(serial, "confirm_small.png", wait_time=0.5)
    main_stage_enter_menu(serial)
    if not wait_click(serial, "treasure_icon.png", timeout=40.0):
        raise GameError("無法進入寶物")

    if not wait(serial, "treasure_text.png", timeout=30.0):
        raise GameError("不在寶物室，強制停止")
    if wait_click(serial, "skip.png", timeout=20.0):
        wait_click(serial, "confirm_small.png", wait_time=0.5)

    if wait_click(serial, "back.png", timeout=20.0):
        wait_click(serial, "confirm_small.png", wait_time=0.5)

    main_stage_finish_new(serial)
    wait_click(serial, "back.png", timeout=10.0)
    on_main_view(serial, sign="back.png", vanish=True)

    if wait_click(serial, "skip.png", timeout=5):
        wait_click(serial, "confirm_small.png", wait_time=0.5)

    wait_click(serial, "long_quest.png", timeout=7.0)
    wait_click(serial, "close_board.png", timeout=10.0)

def seven_days(serial):
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

def upgrade_sheep(serial):
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
    try:
        login_second(serial)
    except GameError as e:
        raise
    try:
        second_stage(serial)
    except GameError as e:
        raise
    try:
        claim_treasure(serial)
    except GameError as e:
        raise
    try:
        main_stage_finish_new(serial)
    except GameError as e:
        raise
    
    try:
        seven_days(serial)
    except GameError as e:
        raise
    try:
        main_stage_finish_new(serial)
    except GameError as e:
        raise
    try:
        upgrade_sheep(serial)
    except GameError as e:
        raise
    try:
        main_stage_finish_new(serial)
    except GameError as e:
        raise
    try:
        back_to_close_board(serial)
    except GameError as e:
        raise
