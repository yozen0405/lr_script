from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from scripts.shared.constants import Settlement, Confirm, Battle, Leonard, Retry, MainView, Positions
from scripts.shared.utils.retry import connection_retry
from scripts.shared.utils.game_view import on_main_view
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
from scripts.shared.events.teams.enum import Teams
from scripts.shared.events.season_pass.enum import SeasonPassImg
from scripts.shared.events.guild.base import guild_raid_battle
from scripts.shared.events.main_stage.selector import main_stage_finish_custom
from scripts.shared.events.advent_stage.base import advent_stage_battle
from scripts.shared.events.bingo.base import bingo_attempt
from scripts.shared.events.login.base import guest_login
from scripts.shared.utils.game_view import on_main_view
from scripts.shared.events.lab.base import complete_lab_quest
from scripts.shared.events.season_pass.base import claim_season_pass
from scripts.shared.events.wheel.base import wheel_attempt
from scripts.shared.events.train.base import train_stage_battle
from scripts.shared.events.dice.base import dice_attempt
from scripts.shared.events.teams.base import upgrade_ranger
import time
from scripts.custom_scripts.pvp_test.base import JobRunner
from scripts.custom_scripts.pvp_test.jobs import (
    LabJob, AdventJob, MainStageJob, 
    GuildRaidJob, PvPJob, SpecialStageJob, 
    TrainJob, SeasonPassJob, DiceJob, UpgradeRangerJob
)

def detect(serial):
    if exist(serial, MainView.BOARD_DONT_SHOW.value):
        print("Main View Detected")

def normal_stage(serial):
    runner = JobRunner(serial)

    # detect(serial)

    runner.restart_game()
    # apply_mode(serial, mode_name="pre_stage", state="on")

    # runner.add_job(LabJob())
    # runner.add_job(AdventJob())
    # runner.add_job(MainStageJob())
    # runner.add_job(GuildRaidJob())
    # runner.add_job(PvPJob())
    # runner.add_job(SpecialStageJob())
    # runner.add_job(TrainJob())
    
    # runner.add_job(UpgradeRangerJob())
    
    # runner.add_job(SeasonPassJob())
    # runner.add_job(DiceJob())

    # runner.execute_all()