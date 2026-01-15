from abc import ABC, abstractmethod
import logging
from core.actions.vision import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from core.actions.system import force_close
from scripts.shared.constants import Settlement, Confirm, Battle, Leonard, Retry, MainView, Positions
from scripts.shared.utils.retry import connection_retry
from scripts.shared.events.pvp.sec import pvp_loop_battle
from scripts.shared.utils.hacks import apply_mode
from scripts.shared.events.special_stage.base import special_stage_single_game, special_stage_loop_game, special_stage_conquer_planet
from scripts.shared.events.special_stage.enum import Planet
from scripts.shared.events.main_stage.enum import MainStageImg
from scripts.shared.events.special_stage.enum import SpecialStage
from scripts.shared.events.pvp.enum import PvPImg
from scripts.shared.events.guild.enum import Guild
from scripts.shared.events.advent_stage.enum import AdventImg
from scripts.shared.events.advent_stage.enum import AdventStageName
from scripts.shared.events.lab.enum import MakeMenu
from scripts.shared.events.dice.enum import DiceImg
from scripts.shared.events.teams.enum import TeamsImg
from scripts.shared.events.teams.base import upgrade_ranger, gear_enhance
from scripts.shared.events.guild.base import guild_raid_battle
from scripts.shared.events.main_stage.base import main_stage_finish_custom
from scripts.shared.events.advent_stage.base import run_advent_stage
from scripts.shared.events.bingo.base import bingo_attempt
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
        super().__init__(name="Lab Quest", mode_name="pre_stage") 

    def run(self, ctx: GameContext):
        complete_lab_quest(ctx.serial)


class AdventJob(BaseJob):
    def __init__(self):
        super().__init__(name="Advent Stage", mode_name="advent")

    def run(self, ctx: GameContext):
        run_advent_stage(ctx.serial)


class MainStageJob(BaseJob):
    def __init__(self):
        super().__init__(name="Main Stage Farming", mode_name="main_stage")

    def run(self, ctx: GameContext):
        main_stage_finish_custom(ctx, custom_stage=323, multiplier=2)


class GuildRaidJob(BaseJob):
    def __init__(self):
        super().__init__(name="Guild Raid", mode_name="guild_raid")

    def run(self, ctx: GameContext):
        guild_raid_battle(ctx.serial)


class PvPJob(BaseJob):
    def __init__(self):
        super().__init__(name="PVP Arena", mode_name="pvp")

    def run(self, ctx: GameContext):
        pvp_loop_battle(ctx)


class SpecialStageJob(BaseJob):
    def __init__(self):
        super().__init__(name="Special Stage", mode_name="special_stage")

    def run(self, ctx: GameContext):
        special_stage_loop_game(ctx, planet=Planet.EVO_MINE.value, stage=6)
        # special_stage_conquer_planet(ctx, planet=Planet.COLLAB.value)
        # for stage in range(4, 7):
        #     special_stage_loop_game(ctx, planet=Planet.IMMORTAL_SKULL.value, stage=stage)


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