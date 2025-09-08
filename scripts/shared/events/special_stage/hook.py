import time
from core.system.logger import log_msg
from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, get_pos, drag
from core.base.exceptions import GameError
from scripts.shared.constants import Settlement, Confirm, Battle, Retry, MainView, Positions
from scripts.shared.events.main_stage.enum import MainStage
from scripts.shared.events.special_stage.enum import SpecialStage
from scripts.shared.utils.retry import connection_retry
from typing import Optional, Tuple

class SpecialStageHooks:
    def __init__(self, serial):
        self.serial = serial

    def on_start_page(self):
        if not wait_click(self.serial, SpecialStage.CIRCLE.value, timeout=3.0, wait_time=1.5):
            return
        wait_click(self.serial, SpecialStage.CIRCLE.value, wait_time=1.5)

    def on_pre_anime(self):
        for _ in range(7):
            if exist(self.serial, SpecialStage.TEXT.value):
                break
            if not wait_click(self.serial, Battle.ANIME.value, wait_time=2.0, threshold=0.6):
                break

    def handle_team_num(self, ctx):
        if not exist_click(self.serial, SpecialStage.TEAM_BTN.value):
            return
        if exist_click(self.serial, SpecialStage.TEAM_NUM_ON(num=ctx.team_num), threshold=0.99):
            return
        exist_click(self.serial, SpecialStage.TEAM_NUM_OFF(num=ctx.team_num), threshold=0.9)