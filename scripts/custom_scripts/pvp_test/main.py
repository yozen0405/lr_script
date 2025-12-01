from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from scripts.shared.constants import Settlement, Confirm, Battle, Leonard, Retry, MainView, Positions
from scripts.shared.utils.retry import connection_retry
from scripts.shared.events.pvp.base import pvp_loop_battle
from scripts.shared.utils.hacks import apply_mode
from scripts.shared.events.special_stage.selector import special_stage_single_game, special_stage_loop_game, special_stage_conquer_planet
from scripts.shared.events.special_stage.enum import Planet
from scripts.shared.events.main_stage.enum import MainStage
from scripts.shared.events.special_stage.enum import SpecialStage
from scripts.shared.events.pvp.enum import PvP
from scripts.shared.events.guild.enum import Guild
from scripts.shared.events.advent_stage.enum import Advent
from scripts.shared.events.advent_stage.enum import AdventStageName
from scripts.shared.events.lab.enum import MakeMenu
from scripts.shared.events.dice.enum import DiceImg
from scripts.shared.events.guild.base import guild_raid_battle
from scripts.shared.events.main_stage.selector import main_stage_finish_custom
from scripts.shared.events.advent_stage.base import advent_stage_battle
from scripts.shared.events.bingo.base import bingo_attempt
from scripts.shared.events.login import guest_login
from scripts.shared.utils.game_view import on_main_view
from scripts.shared.events.lab.base import complete_lab_quest
from scripts.shared.events.season_pass.base import claim_season_pass
from scripts.shared.events.wheel.base import wheel_attempt
from scripts.shared.events.train.base import train_stage_battle
from scripts.shared.events.dice.base import dice_attempt
import time

def normal_stage(serial):
    # complete_lab_quest(serial)
    # wait_click(serial, "back.png")
    # connection_retry(serial, appear="main_stage_btn.png", timeout=40.0)

    # apply_mode(serial, mode_name="advent", state="on")
    # advent_stage_battle(serial, repeat=3)
    # apply_mode(serial, mode_name="advent", state="off")
    # wait_click(serial, "back.png")
    # connection_retry(serial, appear="main_stage_btn.png", timeout=40.0)

    # apply_mode(serial, mode_name="main_stage", state="on")
    # for _ in range(3):
    #     main_stage_finish_custom(serial, custom_stage=26, multiplier=2)
    # apply_mode(serial, mode_name="main_stage", state="off")
    # wait_click(serial, "back.png")
    # connection_retry(serial, appear="main_stage_btn.png", timeout=40.0)

    # apply_mode(serial, mode_name="guild_raid", state="on")
    # guild_raid_battle(serial)
    # apply_mode(serial, mode_name="guild_raid", state="off")
    # wait_click(serial, "back.png")
    # connection_retry(serial, appear="main_stage_btn.png", timeout=40.0)
    # apply_mode(serial, mode_name="pvp", state="on")
    # for i in range(5):
    #     if not pvp_loop_battle(serial):
    #         break
    # apply_mode(serial, mode_name="pvp", state="off")
    # apply_mode(serial, mode_name="special_stage", state="on")
    # wait_click(serial, "back.png")
    # connection_retry(serial, appear="main_stage_btn.png", timeout=40.0)
    # special_stage_conquer_planet(serial, planet=Planet.COLLAB.value)
    # for stage in range(4, 7):
    #     special_stage_loop_game(serial, planet=Planet.IMMORTAL_SKULL.value, stage=stage)
    # wait_click(serial, "back.png")
    # connection_retry(serial, appear="main_stage_btn.png", timeout=40.0)

    # apply_mode(serial, mode_name="train", state="on")
    # train_stage_battle(serial)
    # apply_mode(serial, mode_name="train", state="off")
    # wait_click(serial, "back.png")
    # connection_retry(serial, appear="main_stage_btn.png", timeout=40.0)


    # claim_season_pass(serial)

    # wait_click(serial, "back.png")
    # connection_retry(serial, appear="main_stage_btn.png", timeout=40.0)
    # dice_attempt(serial)


    # wheel_attempt(serial)