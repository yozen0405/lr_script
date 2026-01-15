from scripts.shared.controller.context import GameContext
from scripts.shared.events.special_stage.session import SpecialStageSession
from scripts.shared.events.special_stage.enum import SpecialStage
from scripts.shared.events.main_stage.enum import MainStageImg
from scripts.shared.constants import Battle, Confirm, Retry, MainView
from core.actions.vision import wait_click, exist_click, exist, wait
from core.base.exceptions import GameError

class SpecialStagePrepUtils:
    def __init__(self, context: GameContext, session: SpecialStageSession):
        self.ctx = context
        self.session = session

    def handle_team_num(self):
        if not exist_click(self.ctx.serial, MainStageImg.TEAM_BTN_HIGH.value, wait_time=1.5):
            return
        if exist_click(self.ctx.serial, MainStageImg.TEAM_NUM_HIGH_ON(num=self.session.team_num), threshold=0.999):
            return
        elif exist_click(self.ctx.serial, MainStageImg.TEAM_NUM_HIGH_OFF(num=self.session.team_num), threshold=0.9):
            return
        elif exist_click(self.ctx.serial, MainStageImg.TEAM_NUM_HIGH_OFF(num=1), threshold=0.9):
            return
        elif not exist_click(self.ctx.serial, MainStageImg.TEAM_NUM_LOW_DEFAULT.value, threshold=0.9):
            raise GameError("無法設定隊伍人數")
        
    def handle_auto_btn(self):
        if exist(self.ctx.serial, MainStageImg.AUTO_BTN_HIGH_OFF.value, threshold=0.85):
            exist_click(self.ctx.serial, MainStageImg.AUTO_BTN_HIGH_OFF.value, threshold=0.85)
            return
        if exist(self.ctx.serial, MainStageImg.AUTO_BTN_HIGH_ON.value, threshold=0.85):
            return
        
    def handle_cycle_btn(self):
        wait_click(self.ctx.serial, MainStageImg.CYCLE_HIGH.value)
        wait_click(self.ctx.serial, Battle.MAX_OFF.value, wait_time=1.0)
        if not wait_click(self.ctx.serial, Confirm.SMALL.value):
            raise GameError("無法設定迴圈戰鬥")

    def configure_battle_settings(self):
        self.handle_auto_btn()
        self.handle_team_num()
        if self.session.is_loop_mode:
            self.handle_cycle_btn()
