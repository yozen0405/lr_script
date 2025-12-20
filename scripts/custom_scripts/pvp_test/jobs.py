from abc import ABC, abstractmethod
import logging
from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from core.actions.system import force_close
from scripts.shared.constants import Settlement, Confirm, Battle, Leonard, Retry, MainView, Positions
from scripts.shared.utils.retry import connection_retry
from scripts.shared.utils.game_view import on_main_view, close_board
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
from scripts.shared.events.teams.enum import TeamsImg
from scripts.shared.events.teams.base import upgrade_ranger, gear_enhance
from scripts.shared.events.guild.base import guild_raid_battle
from scripts.shared.events.main_stage.selector import main_stage_finish_custom
from scripts.shared.events.advent_stage.base import advent_stage_battle
from scripts.shared.events.bingo.base import bingo_attempt
from scripts.shared.utils.game_view import on_main_view
from scripts.shared.events.lab.base import complete_lab_quest
from scripts.shared.events.season_pass.sec import claim_season_pass
from scripts.shared.events.wheel.base import wheel_attempt
from scripts.shared.events.train.base import train_stage_battle
from scripts.shared.events.dice.base import dice_attempt
from core.actions.system import log_msg
import time
from scripts.custom_scripts.pvp_test.base import BaseJob
from scripts.shared.controller.context import GameContext

class LabJob(BaseJob):
    def __init__(self):
        super().__init__(name="Lab Quest", mode_name=None) 

    def run(self, ctx: GameContext):
        complete_lab_quest(ctx.serial)


class AdventJob(BaseJob):
    def __init__(self):
        super().__init__(name="Advent Stage", mode_name="advent")

    def run(self, ctx: GameContext):
        advent_stage_battle(ctx.serial, repeat=3)


class MainStageJob(BaseJob):
    def __init__(self):
        super().__init__(name="Main Stage Farming", mode_name="main_stage")

    def run(self, ctx: GameContext):
        for _ in range(3):
            main_stage_finish_custom(ctx, custom_stage=26, multiplier=2)


class GuildRaidJob(BaseJob):
    def __init__(self):
        super().__init__(name="Guild Raid", mode_name="guild_raid")

    def run(self, ctx: GameContext):
        guild_raid_battle(ctx.serial)


class PvPJob(BaseJob):
    def __init__(self):
        super().__init__(name="PVP Arena", mode_name="pvp")

    def run(self, ctx: GameContext):
        for i in range(5):
            if not pvp_loop_battle(ctx.serial):
                break


class SpecialStageJob(BaseJob):
    def __init__(self):
        super().__init__(name="Special Stage", mode_name="special_stage")

    def run(self, ctx: GameContext):
        # special_stage_loop_game(ctx.serial, planet=Planet.COLLAB.value, stage=6)
        # special_stage_conquer_planet(ctx, planet=Planet.COLLAB.value)
        # for stage in range(4, 7):
        #     special_stage_loop_game(ctx.serial, planet=Planet.IMMORTAL_SKULL.value, stage=stage)
        special_stage_conquer_planet(ctx, planet=Planet.COLLAB.value)


class SeasonPassJob(BaseJob):
    def __init__(self):
        super().__init__(name="Claim Season Pass", mode_name=None)

    def run(self, ctx: GameContext):
        claim_season_pass(ctx)

class BingoJob(BaseJob):
    def __init__(self):
        super().__init__(name="Bingo Attempt", mode_name=None)

    def run(self, ctx: GameContext):
        bingo_attempt(ctx.serial)

class UpgradeRangerJob(BaseJob):
    def __init__(self):
        super().__init__(name="Upgrade Ranger", mode_name=None)

    def run(self, ctx: GameContext):
        upgrade_ranger(ctx)

class GearEnhanceJob(BaseJob):
    def __init__(self):
        super().__init__(name="Gear Enhance", mode_name=None)

    def run(self, ctx: GameContext):
        gear_enhance(ctx)