from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from scripts.shared.constants import Settlement, Confirm, Battle, Retry
from scripts.shared.utils.retry import connection_retry
from scripts.shared.events.pvp.base import pvp_loop_battle
from scripts.shared.utils.hacks import apply_mode
from scripts.shared.events.special_stage.selector import special_stage_single_game, special_stage_loop_game
from scripts.shared.events.special_stage.enum import Planet

def normal_stage(serial):
    # apply_mode(serial, mode_name="pvp", state="on")
    # for _ in range(5):
    #     if not pvp_loop_battle(serial):
    #         break
    apply_mode(serial, mode_name="pvp", state="off")
    apply_mode(serial, mode_name="special_stage", state="on")
    wait(serial, "back.png")
    connection_retry(serial, wait_name="main_stage_btn.png", timeout=40.0)
    special_stage_loop_game(serial, planet=Planet.COLLAB)