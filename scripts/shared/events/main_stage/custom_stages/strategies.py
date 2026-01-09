import time
from core.system.logging.logger import log_msg
from core.actions.vision import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from core.actions.vision import get_main_stage_num
from core.base.exceptions import GameError
from scripts.shared.constants.positions import Positions
from scripts.shared.controller.context import GameContext
from scripts.shared.events.main_stage.custom_stages.base import MainStageCustomHookBase
from scripts.shared.events.main_stage.session import StageSession
from scripts.shared.utils.retry import connection_retry
from typing import Optional
from scripts.shared.constants import Settlement, Battle, Confirm, MainView, Leonard, Retry
from scripts.shared.events.main_stage.enum import MainStageImg, Stages, Treasure
from scripts.shared.events.main_stage.custom_stages.enum import Stage13Img, Stage3Img, Stage1Img

class FirstStage(MainStageCustomHookBase):
    def on_preperation_start(self):
        wait_click(self.ctx.serial, Stage1Img.METEOR.value, threshold=0.8)

    def on_battle_start(self):
        if exist(self.ctx.serial, Stage1Img.TUTORIAL_TEXT.value, threshold=0.9):
            wait_click(self.ctx.serial, Positions.METEOR.value)

class ThirdStage(MainStageCustomHookBase):
    def on_battle_start(self):
        if exist(self.ctx.serial, Leonard.BG_HAPPY.value, threshold=0.8):
            wait_click(self.ctx.serial, Stage3Img.SPEED_BTN_OFF.value)

        if exist(self.ctx.serial, Leonard.BG_JUMP.value, threshold=0.8):
            wait_click(self.ctx.serial, Stage3Img.SPEED_BTN_ON.value)

        exist_click(self.ctx.serial, Stage3Img.SPEED_BTN_OFF.value, threshold=0.8)

class AutoStage(MainStageCustomHookBase):
    def on_battle_start(self):
        if exist(self.ctx.serial, Leonard.BG_HAPPY.value, threshold=0.8):
            wait_click(self.ctx.serial, Stage13Img.AUTO_BTN_ON.value)

        if exist(self.ctx.serial, Leonard.BG_JUMP.value, threshold=0.8):
            wait_click(self.ctx.serial, Stage13Img.AUTO_BTN_OFF.value)

        exist_click(self.ctx.serial, Stage13Img.AUTO_BTN_OFF.value, threshold=0.8)  

class FriendStage(MainStageCustomHookBase):
    def on_preperation_start(self):
        if exist_click(self.ctx.serial, MainView.SKIP.value):
            wait_click(self.ctx.serial, Confirm.SMALL.value, wait_time=1.0)
        else:
            return
        wait_click(self.ctx.serial, MainView.SKIP.value, timeout=5.0, wait_time=1.0)
        loc = get_pos(self.ctx.serial, MainStageImg.JAMES_FRIEND.value)
        if loc is not None:
            x, y = loc
        else:
            raise GameError("無法找到好友位置")
        wait_click(self.ctx.serial, (x, y - 50), wait_time=1.0)

    def on_battle_start(self):
        if exist(self.ctx.serial, Leonard.BG_CLAP.value, threshold=0.8):
            wait_click(self.ctx.serial, Positions.FRIEND)

        if exist_click(self.ctx.serial, MainView.SKIP.value):
            wait_click(self.ctx.serial, Confirm.SMALL.value, timeout=3.0)

    