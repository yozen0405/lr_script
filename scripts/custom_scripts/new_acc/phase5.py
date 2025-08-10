import time
import os
from core.system.logger import log_msg
from core.actions.actions import (
    wait_click, exist_click, exist,
    wait, wait_vanish,
    back, drag, force_close,
    get_pos
)
from core.base.exceptions import GameError
from scripts.shared.utils.game_view import close_board
from scripts.shared.utils.retry import connection_retry
from scripts.shared.utils.game_boot import open_game_with_hacks
from scripts.shared.utils.game_view import on_main_view
from scripts.shared.events.main_stage.selector import main_stage_finish_new, main_stage_finish_custom

def james_friend(serial):
    on_main_view(serial)
    if wait_click(serial, "skip.png", timeout=5.0):
        wait_click(serial, "confirm_small.png", wait_time=3.0)
    main_stage_finish_new(serial)

def stage30(serial):
    main_stage_finish_custom(serial, custom_stage="stage30_btn.png")

def do_team_upgrade(serial):
    if not wait_click(serial, "back.png"):
        raise GameError("未知狀態")
    on_main_view(serial)
    
    wait_click(serial, "team_icon.png")
    connection_retry(serial, wait_name="team_text.png", exception_msg="進不去隊伍", timeout=40.0)
    wait_click(serial, "leonard_teacher_switch_team.png")
    wait_click(serial, "leonard_teacher_switch_team2.png", wait_time=2.0)
    wait_click(serial, "jessica_upgrade_ranger.png", wait_time=1.5)
    wait_click(serial, "upgrade_btn.png")
    connection_retry(serial, wait_name="back.png", exception_msg="無法進入升級頁面", timeout=40.0, wait_time=3.0)
    for _ in range(2):
        drag(serial, (449, 605), (449, 357), timeout=10.0)
    wait_click(serial, "upgrade_lvl_btn.png")
    if not wait_click(serial, "confirm_small.png", wait_time=3.0):
        raise GameError("升級失敗")
    
    connection_retry(serial, wait_name="upgrade_success.png", exception_msg="無法升級", timeout=40.0)
    for _ in range(3):
        if not wait_click(serial, "upgrade_success.png", timeout=5.0, wait_time=1.0):
            break
    wait_click(serial, "back.png")
    wait(serial, "team_text.png", timeout=20.0)
    wait_click(serial, "back.png", timeout=20.0)
    connection_retry(serial, image_name="back.png", timeout=40.0)

def do_diamond_upgrade(serial):
    on_main_view(serial)
    wait_click(serial, "diamond_upgrade_icon.png")
    connection_retry(serial, wait_name="diamond_upgrade_text.png", exception_msg="無法進入科技升級", timeout=40.0)
    pos = get_pos(serial, "diamond_upgrade_text.png")
    if pos:
        x, y = pos
    else:
        raise GameError("找不到升級文字")

    wait_click(serial, (x, y + 350))
    if not wait_click(serial, "diamond_upgrade_max.png"):
        raise GameError("無法升級")

    for _ in range(7):
        wait_click(serial, "diamond_upgrade_minus.png")
    wait_click(serial, "confirm_small.png", wait_time=1.0)

    for _ in range(3):
        wait_click(serial, "diamond_upgrade_success.png", timeout=5.0, wait_time=1.0)
        if wait_click(serial, "back.png"):
            break
    connection_retry(serial, image_name="back.png", timeout=40.0)

def claim_seven_day(serial):
    on_main_view(serial)

    wait_click(serial, "7days.png")
    connection_retry(serial, wait_name="7day_quest_reward.png", exception_msg="無法進入7天登入", timeout=40.0)
    pos = get_pos(serial, "7day_quest_reward.png")
    if pos:
        x, y = pos
    else:
        raise GameError("找不到升級文字")

    wait_click(serial, (x + 500, y), wait_time=1.0)
    wait_click(serial, "confirm_small.png", timeout=10.0)
    wait_click(serial, "7day_daily_reward.png", timeout=10.0, wait_time=1.0)
    wait_click(serial, "confirm_small.png", timeout=10.0)
    if not wait(serial, "7day_daily_claimed.png"):
        raise GameError("沒領到扭蛋卷")
    wait_click(serial, "close_board.png")

def claim_season_pass(serial):
    on_main_view(serial)
    wait_click(serial, "season_pass_icon.png", timeout=7.0)
    connection_retry(serial, wait_name="confirm_small.png", exception_msg="無法進入季票", timeout=40.0)
    wait_click(serial, "confirm_small.png", timeout=10.0)

    if not wait_click(serial, "leonard_teacher_circle.png"):
        raise GameError("並非首次進入季票")
    wait_click(serial, "leonard_teacher_circle.png")
    for _ in range(10):
        wait_click(serial, "season_pass_text.png", wait_time=1.5)

    wait(serial, "season_pass_text.png", timeout=10.0, threshold=0.99)
    wait_click(serial, "daily_quest_nav.png", timeout=10.0)
    for _ in range(3):
        if wait_click(serial, "daily_quest_claim.png", wait_time=2.0):
            wait_click(serial, "confirm_small.png", wait_time=2.0)
    wait_click(serial, "weekly_quest_nav.png", timeout=10.0, wait_time=1.0)
    if wait_click(serial, "daily_quest_claim.png", wait_time=2.0):
        wait_click(serial, "confirm_small.png", wait_time=2.0)

    if wait(serial, "season_pass_text.png", timeout=10.0, threshold=0.99):
        wait_click(serial, "season_pass_nav.png", timeout=10.0, wait_time=1.0)
        wait_click(serial, "season_pass_tickets.png", timeout=10.0, wait_time=2.0)
        wait_click(serial, "confirm_big.png", wait_time=2.0, threshold=0.65)
        if wait(serial, "season_pass_level1_text.png", timeout=60.0):
            wait_click(serial, "close_board.png", timeout=10.0)
        else:
            raise GameError("季票領取獎勵錯誤")
    else:
        raise GameError("季票領取獎勵錯誤")
    wait_click(serial, "back.png")
    connection_retry(serial, image_name="back.png", timeout=40.0)
    on_main_view(serial)


def phase5(serial):
    log_msg(serial, "第五階段")

    for _ in range(4):
        try:
            main_stage_finish_new(serial)
        except GameError as e:
            raise

    try:
        james_friend(serial)
    except GameError as e:
        raise

    try:
        stage30(serial)
    except GameError as e:
        raise

    try:
        do_team_upgrade(serial)
    except GameError as e:
        raise

    try:
        do_diamond_upgrade(serial)
    except GameError as e:
        raise

    try:
        claim_seven_day(serial)
    except GameError as e:
        raise

    try:
        claim_season_pass(serial)
    except GameError as e:
        raise
    