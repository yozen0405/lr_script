import time
import os
from core.system.logger import log_msg
from core.actions.actions import (
    wait_click, exist_click, exist, wait,
    wait_vanish, extract_text, back, drag,
     match_string_from_region, get_clipboard_text,
     pull_account_file, clear_game_storage,
     force_close
)
from scripts.shared.utils.retry import connection_retry
from scripts.shared.utils.game_boot import open_game_with_hacks
from scripts.shared.utils.game_view import on_main_view
from scripts.shared.events.gacha import Gacha
from core.base.exceptions import GameError

def claim_tickets(serial):
    on_main_view(serial)

    if wait_click(serial, "skip.png", timeout=5.0):
        wait_click(serial, "confirm_small.png", wait_time=3.0)
    
    wait_click(serial, "gift_btn.png", timeout=7.0, wait_time=2.0)
    
    if not wait_click(serial, "accept_all.png", timeout=15.0):
        wait_click(serial, "close_board.png")
        
    wait_click(serial, "confirm_small.png", timeout=15.0, wait_time=3.0)
    wait_click(serial, "confirm_small.png", wait_time=1.5)
    wait_click(serial, "close_board.png", wait_time=1.5)

    if wait_click(serial, "skip.png", timeout=15.0):
        wait_click(serial, "confirm_small.png", wait_time=1.0)
    wait_click(serial, "skip.png", timeout=3.0)


def gacha_pull(serial):
    gacha = Gacha(serial)
    gacha.enter_gacha()
    gacha.pull()
    force_close(serial)
    clear_game_storage(serial)

def phase6(serial):
    log_msg(serial, "第六階段")
    try:
        claim_tickets(serial)
    except GameError as e:
        raise

    try:
        gacha_pull(serial)
    except GameError as e:
        raise