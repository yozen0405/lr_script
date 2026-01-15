import time
from core.system.logging.logger import log_msg
from core.actions.vision import (
    wait_click, exist_click, exist,
      wait, wait_vanish, drag, get_pos, 
      check_region_brightness,
)
from core.actions.vision import get_main_stage_num
from core.base.exceptions import GameError
from scripts.shared.constants.positions import Positions
from scripts.shared.utils.retry import connection_retry
from typing import Optional
from scripts.shared.constants import Settlement, Battle, Confirm, MainView, Leonard, Retry
from scripts.shared.events.main_stage.enum import MainStageImg, Stages, Treasure
from scripts.shared.controller.context import GameContext
from scripts.shared.events.advent_stage.enum import AdventImg
from scripts.shared.events.advent_stage.session import AdventStageSession
from scripts.shared.utils.hacks import apply_mode

class PreperationUtils:
    def __init__(self, context: GameContext, session: AdventStageSession):
        self.ctx = context
        self.session = session

    def handle_team_num(self):
        if not exist_click(self.ctx.serial, AdventImg.TEAM_BTN.value, wait_time=1.5):
            return
        if exist_click(self.ctx.serial, MainStageImg.TEAM_NUM_LOW_ON(num=self.session.team_num), threshold=0.999):
            return
        elif exist_click(self.ctx.serial, MainStageImg.TEAM_NUM_LOW_OFF(num=self.session.team_num), threshold=0.9):
            return
        elif exist_click(self.ctx.serial, MainStageImg.TEAM_NUM_LOW_OFF(num=1), threshold=0.9):
            return
        elif not exist_click(self.ctx.serial, MainStageImg.TEAM_NUM_LOW_DEFAULT.value, threshold=0.9):
            raise GameError("無法設定隊伍人數")
        
    def handle_auto_btn(self):
        if exist(self.ctx.serial, AdventImg.AUTO_BTN_OFF.value, threshold=0.85):
            exist_click(self.ctx.serial, AdventImg.AUTO_BTN_OFF.value, threshold=0.85)
            return
        if exist(self.ctx.serial, AdventImg.AUTO_BTN_ON.value, threshold=0.85):
            return
        
    def handle_cycle_btn(self):
        wait_click(self.ctx.serial, AdventImg.CYCLE.value)
        for _ in range(self.session.repeat - 1):
            wait_click(self.ctx.serial, AdventImg.PLUS.value, wait_time=0.0)
        wait_click(self.ctx.serial, Confirm.SMALL.value)

    def configure_battle_settings(self):
        self.handle_auto_btn()
        self.handle_team_num()

    