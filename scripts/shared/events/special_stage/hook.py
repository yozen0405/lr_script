import time
from core.system.logging.logger import log_msg
from core.actions.vision import wait_click, exist_click, exist, wait, wait_vanish, get_pos, drag
from core.base.exceptions import GameError
from scripts.shared.constants import Settlement, Confirm, Battle, Retry, MainView, Positions
from scripts.shared.events.main_stage.enum import MainStageImg
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
        start_time = time.time()    
        while time.time() - start_time < 80:
            if exist(self.serial, SpecialStage.TEXT.value):
                break
            if exist(self.serial, Retry.TEXT1.value):
                exist_click(self.serial, Retry.BTN.value)
                continue
            exist_click(self.serial, Battle.ANIME.value, threshold=0.6)

    def handle_team_num(self, ctx):
        if not exist_click(self.serial, SpecialStage.TEAM_BTN.value):
            return
        if exist_click(self.serial, SpecialStage.TEAM_NUM_ON(num=ctx.team_num), threshold=0.99):
            return
        elif exist_click(self.serial, SpecialStage.TEAM_NUM_OFF(num=ctx.team_num), threshold=0.9):
            return
        elif not exist_click(self.serial, SpecialStage.TEAM_NUM_ON(num=1), threshold=0.9):
            raise GameError("無法設定隊伍人數")
        
    def handle_auto_btn(self, base):
        exist_click(self.serial, MainStageImg.AUTO_BTN_HIGH_OFF.value, threshold=0.99)