import time
import os
from core.system.logger import log_msg
from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, back, drag, find_spotlight_center
from scripts.shared.events.gacha.base import on_gacha_event
from core.base.exceptions import GameError
from scripts.shared.constants import MainView, Confirm, Retry
from scripts.shared.utils.retry import connection_retry
import time
from scripts.shared.events.main_stage.selector import on_main_stage_event    
from scripts.shared.events.teams.base import on_team_event, on_upgrade_event
from scripts.shared.events.seven_days.base import seven_days_event
from scripts.shared.events.special_stage.selector import on_special_stage_event
from core.actions.screen import wait_click, exist_click, exist, wait, get_pos, check_region_brightness
from scripts.shared.events.special_quest.base import special_quest_event
from core.base.exceptions import GameError
from scripts.shared.events.season_pass.enum import SeasonPassImg
from scripts.shared.constants import MainView
from typing import List
from scripts.shared.controller.context import GameContext
from scripts.shared.utils.mainview.enum import MainViewState
from scripts.shared.events.main_stage.enum import MainStage
from scripts.shared.events.special_stage.enum import SpecialStage
from scripts.shared.events.seven_days.enum import SevenDaysImg
from scripts.shared.events.special_quest.enum import SpecialQuestImg
from scripts.shared.events.gacha.enum import GachaImg
from scripts.shared.events.teams.enum import TeamsImg

class EventStrategy():
    def __init__(self, ctx: GameContext):
        self.ctx = ctx

        self.regions: dict[MainViewState, tuple[int, int, int, int] | None] = {
            MainViewState.MAIN_STAGE: (553, 150, 744, 298),
            MainViewState.SPECIAL_STAGE: (187, 258, 457, 422),
            MainViewState.SEVEN_DAYS: (1173, 368, 1271, 467),
            MainViewState.SPECIAL_QUEST: (1177, 271, 1271, 359),
            MainViewState.TEAM: (203, 592, 305, 683),
            MainViewState.UPGRADE: (533, 355, 706, 483),
            MainViewState.GACHA: (798, 79, 971, 237),
        }

    def handle_event(self, state: MainViewState):
        if state == MainViewState.GACHA:
            on_gacha_event(self.ctx)
        elif state == MainViewState.MAIN_STAGE:
            on_main_stage_event(self.ctx)
        elif state == MainViewState.SEVEN_DAYS:
            seven_days_event(self.ctx)
        elif state == MainViewState.SPECIAL_QUEST:
            special_quest_event(self.ctx)
        elif state == MainViewState.SPECIAL_STAGE:
            on_special_stage_event(self.ctx)
        elif state == MainViewState.TEAM:
            on_team_event(self.ctx)
        elif state == MainViewState.UPGRADE:
            on_upgrade_event(self.ctx)
        else:
            raise GameError(f"Unsupported event state: {state}")

    def detect(self) -> MainViewState:
        if exist(self.ctx.serial, MainView.TO_DOWNLOAD_TEXT.value, threshold=0.9):
            return MainViewState.TO_DOWNLOAD

        if exist(self.ctx.serial, MainStage.BTN.value, threshold=0.9) and \
           check_region_brightness(self.ctx.serial, self.regions[MainViewState.MAIN_STAGE], threshold=50):
            return MainViewState.MAIN_STAGE

        if exist(self.ctx.serial, SpecialStage.BTN.value, threshold=0.9) and \
           check_region_brightness(self.ctx.serial, self.regions[MainViewState.SPECIAL_STAGE], threshold=50):
            return MainViewState.SPECIAL_STAGE
        
        if exist(self.ctx.serial, SevenDaysImg.BTN.value, threshold=0.9) and \
           check_region_brightness(self.ctx.serial, self.regions[MainViewState.SEVEN_DAYS], threshold=50):
            return MainViewState.SEVEN_DAYS
        
        if exist(self.ctx.serial, SpecialQuestImg.BTN.value, threshold=0.9) and \
           check_region_brightness(self.ctx.serial, self.regions[MainViewState.SPECIAL_QUEST], threshold=50):
            return MainViewState.SPECIAL_QUEST

        if exist(self.ctx.serial, TeamsImg.BTN.value, threshold=0.9) and \
           check_region_brightness(self.ctx.serial, self.regions[MainViewState.TEAM], threshold=50):
            return MainViewState.TEAM
        
        if (exist(self.ctx.serial, TeamsImg.RENE_MAINVIEW.value) or \
            exist(self.ctx.serial, TeamsImg.SHEEP_MAINVIEW.value)) and \
              check_region_brightness(self.ctx.serial, self.regions[MainViewState.UPGRADE], threshold=50):
            return MainViewState.UPGRADE
        
        if exist(self.ctx.serial, GachaImg.BTN.value, threshold=0.9) and \
           check_region_brightness(self.ctx.serial, self.regions[MainViewState.GACHA], threshold=50):
            return MainViewState.GACHA

        return MainViewState.UNKNOWN