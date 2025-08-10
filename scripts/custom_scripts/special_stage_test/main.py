from scripts.shared.events.special_stage.selector import special_stage_single_game, special_stage_loop_game
from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from scripts.shared.events.special_stage.enum import Planet
from scripts.shared.constants import Settlement, Confirm, Battle, Retry

def normal_stage(serial):
    special_stage_loop_game(serial, planet=Planet.COLLAB)