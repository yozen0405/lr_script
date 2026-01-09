import time
import os
from core.system.logging.logger import log_msg
from core.actions.vision import wait_click, exist_click, exist, wait, wait_vanish, back, drag, find_spotlight_center
from scripts.shared.events.gacha.base import on_gacha_event
from core.base.exceptions import GameError
from scripts.shared.constants import MainView, Confirm, Retry, GameView
from scripts.shared.utils.retry import connection_retry
import time
from scripts.shared.events.main_stage.base import on_main_stage_event    
from scripts.shared.events.teams.base import on_team_event, on_upgrade_event
from scripts.shared.events.seven_days.base import seven_days_event
from scripts.shared.events.special_stage.selector import on_special_stage_event
from core.actions.vision import wait_click, exist_click, exist, wait, get_pos, check_region_brightness
from scripts.shared.events.special_quest.base import special_quest_event
from core.base.exceptions import GameError
from scripts.shared.events.season_pass.enum import SeasonPassImg
from scripts.shared.constants import MainView
from typing import List
from scripts.shared.controller.context import GameContext
from scripts.shared.utils.mainview.enum import MainViewState
from scripts.shared.events.main_stage.enum import MainStageImg
from scripts.shared.events.special_stage.enum import SpecialStage
from scripts.shared.events.seven_days.enum import SevenDaysImg
from scripts.shared.events.special_quest.enum import SpecialQuestImg
from scripts.shared.events.gacha.enum import GachaImg
from scripts.shared.events.teams.enum import TeamsImg
from scripts.shared.utils.mainview.interrupt.events.detector import EventDetector

class EventStrategy():
    def __init__(self, ctx: GameContext):
        self.ctx = ctx
        self.detector = EventDetector(ctx)

    def handle_main_event(self, state: MainViewState):
        if state == MainViewState.GACHA:
            on_gacha_event(self.ctx)
        elif state == MainViewState.MAIN_STAGE:
            on_main_stage_event(self.ctx)
        elif state == MainViewState.SEVEN_DAYS:
            seven_days_event(self.ctx)
        elif state == MainViewState.SPECIAL_QUEST:
            special_quest_event(self.ctx)
        elif state == MainViewState.TEAM:
            on_team_event(self.ctx)
        elif state == MainViewState.UPGRADE:
            on_upgrade_event(self.ctx)
        else:
            raise GameError(f"Unsupported event state: {state}")

    def detect_main(self) -> MainViewState:
        return self.detector.detect_active_state()
    
    def handle_special_stage(self) -> bool:
        if self.detector.is_special_stage_active():
            on_special_stage_event(self.ctx)
            return True
        return False