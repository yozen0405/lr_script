from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from scripts.shared.constants import Settlement, Confirm, Battle, Retry, MainView, Positions
from scripts.shared.utils.retry import connection_retry
from scripts.shared.events.pvp.base import pvp_loop_battle
from scripts.shared.utils.hacks import apply_mode
from scripts.shared.events.special_stage.selector import special_stage_single_game, special_stage_loop_game, special_stage_conquer_planet
from scripts.shared.events.special_stage.enum import Planet
from scripts.shared.events.main_stage.enum import MainStage
from scripts.shared.events.pvp.enum import PvP
from scripts.shared.events.guild.enum import Guild
from scripts.shared.events.guild.base import guild_raid_battle
from scripts.shared.events.main_stage.selector import main_stage_finish_custom
from scripts.shared.events.advent_stage.base import advent_stage_battle
from scripts.shared.events.bingo.base import bingo_attempt
from scripts.shared.events.login import guest_login
from scripts.shared.utils.game_view import on_main_view
import time

def normal_stage(serial):
    # bingo_attempt(serial)
    # apply_mode(serial, mode_name="advent", state="on")
    # advent_stage_battle(serial)
    # apply_mode(serial, mode_name="advent", state="off")
    # wait_click(serial, "back.png")
    # connection_retry(serial, appear="main_stage_btn.png", timeout=40.0)

    # apply_mode(serial, mode_name="main_stage", state="on")
    for _ in range(2):
        main_stage_finish_custom(serial, custom_stage=27, multiplier=1)
    # apply_mode(serial, mode_name="main_stage", state="off")
    # wait_click(serial, "back.png")
    # connection_retry(serial, appear="main_stage_btn.png", timeout=40.0)

    # apply_mode(serial, mode_name="guild_raid", state="on")
    # guild_raid_battle(serial)
    # apply_mode(serial, mode_name="guild_raid", state="off")
    # wait_click(serial, "back.png")
    # connection_retry(serial, appear="main_stage_btn.png", timeout=40.0)
    # apply_mode(serial, mode_name="pvp", state="on")
    # for _ in range(3):
    #     if not pvp_loop_battle(serial):
    #         break
    # apply_mode(serial, mode_name="pvp", state="off")
    # apply_mode(serial, mode_name="special_stage", state="on")
    # wait_click(serial, "back.png")
    # connection_retry(serial, appear="main_stage_btn.png", timeout=40.0)
    # special_stage_single_game(serial, planet=Planet.COLLAB.value, stage=1)
    # special_stage_loop_game(serial, planet=Planet.COLLAB.value, stage=2)
    # special_stage_loop_game(serial, planet=Planet.COLLAB.value, stage=4)
    # special_stage_loop_game(serial, planet=Planet.COLLAB.value, stage=6)
    # for stage in range(2, 7):
    #     special_stage_loop_game(serial, planet=Planet.IMMORTAL_SKULL.value, stage=stage)
    # wait_click(serial, "back.png")
    # connection_retry(serial, appear="main_stage_btn.png", timeout=40.0)
