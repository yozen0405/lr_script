import time
from core.system.logging.logger import log_msg
from core.actions.vision import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos, check_region_brightness
from core.actions.vision import get_main_stage_num
from core.base.exceptions import GameError
from scripts.shared.constants.positions import Positions
from scripts.shared.events.main_stage.custom_stages.resolver import StageHookResolver
from scripts.shared.utils.retry import connection_retry
from typing import Optional
from scripts.shared.constants import Settlement, Battle, Confirm, MainView, Leonard, Retry
from scripts.shared.events.main_stage.enum import MainStageImg, Stages, Treasure
from scripts.shared.controller.context import GameContext
from scripts.shared.events.main_stage.session import StageSession
from scripts.shared.events.main_stage.modules.preperation.interrupt.mutipiler_tutorial import MultiplierTutorialInterrupt
from scripts.shared.utils.hacks import apply_mode

class PreperationUtils:
    def __init__(self, context: GameContext, session: StageSession):
        self.ctx = context
        self.session = session
        self.mut_interrupt = MultiplierTutorialInterrupt(context)

    def handle_team_num(self):
        if self.session.is_low:
            if not exist_click(self.ctx.serial, MainStageImg.TEAM_BTN_LOW.value, wait_time=1.5):
                return
            if exist_click(self.ctx.serial, MainStageImg.TEAM_NUM_LOW_ON(num=self.session.team_num), threshold=0.999):
                return
            elif exist_click(self.ctx.serial, MainStageImg.TEAM_NUM_LOW_OFF(num=self.session.team_num), threshold=0.9):
                return
            elif exist_click(self.ctx.serial, MainStageImg.TEAM_NUM_LOW_OFF(num=1), threshold=0.9):
                return
            elif not exist_click(self.ctx.serial, MainStageImg.TEAM_NUM_LOW_DEFAULT.value, threshold=0.9):
                raise GameError("無法設定隊伍人數")
        else:
            if not exist_click(self.ctx.serial, MainStageImg.TEAM_BTN_HIGH.value, wait_time=1.5):
                return
            if exist_click(self.ctx.serial, MainStageImg.TEAM_NUM_HIGH_ON(num=self.session.team_num), threshold=0.999):
                return
            exist_click(self.ctx.serial, MainStageImg.TEAM_NUM_HIGH_OFF(num=self.session.team_num), threshold=0.9)

    def handle_multiplier(self):
        if self.session.is_low:
            if not exist(self.ctx.serial,MainStageImg.MUTIPLIER_LOW_OFF_TEXT.value):
                return
        for _ in range(5):
            if self.session.is_low:
                did_found = exist(self.ctx.serial, MainStageImg.MULTIPLIER_LOW_BTN(times=self.session.multiplier), threshold=0.9)
            else:
                did_found = exist(self.ctx.serial, MainStageImg.MULTIPLIER_HIGH_BTN(times=self.session.multiplier), threshold=0.9)

            if did_found:
                return
            exist_click(self.ctx.serial, MainStageImg.MUTIPLIER_LOW_ON_TEXT.value, wait_time=0.5)

    def handle_auto_btn(self):
        if self.session.is_low:
            if exist(self.ctx.serial, MainStageImg.AUTO_BTN_LOW_ON.value, threshold=0.85):
                self.session.has_auto = True
                return
            elif exist(self.ctx.serial, MainStageImg.AUTO_BTN_LOW_OFF.value, threshold=0.85):
                exist_click(self.ctx.serial, MainStageImg.AUTO_BTN_LOW_OFF.value, threshold=0.85)
                self.session.has_auto = True
                return
            else:
                self.session.has_auto = False
        else:
            if exist(self.ctx.serial, MainStageImg.AUTO_BTN_HIGH_ON.value, threshold=0.85):
                self.session.has_auto = True
                return
            elif exist(self.ctx.serial, MainStageImg.AUTO_BTN_HIGH_OFF.value, threshold=0.85):
                exist_click(self.ctx.serial, MainStageImg.AUTO_BTN_HIGH_OFF.value, threshold=0.85)
                self.session.has_auto = True
                return
            else:
                self.session.has_auto = False

    def on_interrupt(self):
        loc = get_pos(self.ctx.serial, MainStageImg.PRE_START_TEXT.value, return_center=False, threshold=0.9)
        if loc:
            if not check_region_brightness(self.ctx.serial, region=loc, threshold=30):
                return True
        return False
    
    def handle_interrupt(self):
        if self.on_interrupt():
            if self.session.is_first:
                self.session.stage_cls.on_preperation_start()
            else:
                if not self.mut_interrupt.handle():
                    raise GameError("無法處理戰鬥準備頁面中斷")

    def configure_current_stage(self):
        self.session.stage_num = get_main_stage_num(self.ctx.serial)
        self.session.stage_cls = StageHookResolver.get_hook(self.session.stage_num, self.ctx)
        self.session.is_low = self.session.stage_num < 100

    def configure_battle_settings(self):
        self.handle_interrupt()
        self.handle_auto_btn()
       
        if not self.session.is_first:
            self.handle_multiplier()
            self.handle_team_num()

    