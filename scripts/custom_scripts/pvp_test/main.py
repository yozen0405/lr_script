from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos, check_region_brightness, find_spotlight_center
from scripts.shared.constants import Settlement, Confirm, Battle, Leonard, Retry, MainView, Positions, GameView
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
from scripts.shared.events.teams.enum import TeamsImg
from scripts.shared.events.season_pass.enum import SeasonPassImg
from scripts.shared.events.teams.enum import GearImg
from scripts.shared.events.guild.base import guild_raid_battle
from scripts.shared.events.main_stage.selector import main_stage_finish_custom
from scripts.shared.events.advent_stage.base import advent_stage_battle
from scripts.shared.events.bingo.base import bingo_attempt
from scripts.shared.utils.game_view import on_main_view
from scripts.shared.events.lab.base import complete_lab_quest
from scripts.shared.events.season_pass.base import claim_season_pass
from scripts.shared.events.wheel.base import wheel_attempt
from scripts.shared.events.train.base import train_stage_battle
from scripts.shared.events.dice.base import dice_attempt
from scripts.shared.events.teams.sec import upgrade_ranger
import time
from scripts.custom_scripts.pvp_test.base import JobRunner
from scripts.custom_scripts.pvp_test.jobs import (
    LabJob, AdventJob, MainStageJob, 
    GuildRaidJob, PvPJob, SpecialStageJob, 
    TrainJob, SeasonPassJob, DiceJob, UpgradeRangerJob,
    GearEnhanceJob
)

def check_brightness(serial):
    (x1, y1, x2, y2) = get_pos(serial, TeamsImg.POP_UP_BASIC_NAV_DARK.value, threshold=0.95, return_center=False)
    if check_region_brightness(serial, region=(x1, y1, x2, y2), threshold=45):
        print("Main View Detected")

def detect(serial):
    if exist_click(serial, TeamsImg.SORT_LATEST.value):
        print("Detect No Avatar Popup")

def normal_stage(serial):
    runner = JobRunner(serial)

    # runner.start_game()

    # detect(serial)
    # check_brightness(serial)
    # apply_mode(serial, mode_name="pre_stage", state="on")

    apply_mode(serial, mode_name="main_stage", state="off")

    # runner.add_job(GearEnhanceJob())
    # runner.add_job(LabJob())
    # runner.add_job(AdventJob())
    # runner.add_job(MainStageJob())
    # runner.add_job(GuildRaidJob())
    runner.add_job(PvPJob())
    # runner.add_job(SpecialStageJob())
    # runner.add_job(TrainJob())
    
    # runner.add_job(UpgradeRangerJob())
    
    runner.add_job(SeasonPassJob())
    runner.add_job(DiceJob())

    runner.execute_all()