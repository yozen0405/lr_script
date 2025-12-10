from scripts.shared.events.main_stage.hooks import MainStageHooks
from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from scripts.shared.utils.retry import connection_retry
import time
from core.base.exceptions import GameError
from core.system.logger import log_msg
from scripts.shared.constants import MainView, Battle, Confirm, Settlement
from scripts.shared.events.main_stage.enum import MainStage
from scripts.shared.constants.leonard import Leonard
from scripts.shared.events.main_stage.base import BaseMainStage

class FirstStage(MainStageHooks):
    def on_pre_start_page_prev(self, base: BaseMainStage):
        wait_click(self.serial, MainStage.METEOR.value, threshold=0.5)

    def on_start_page(self, base: BaseMainStage):
        exist_click(self.serial, MainStage.METEOR_TEXT.value, threshold=0.9)

    def settlement_items(self, base: BaseMainStage):
        return [Settlement.ONE_REWARD.value, Confirm.BIG1.value,Confirm.BIG2.value]

class SecondStage(MainStageHooks):
    def on_settlement_page(self):
        if exist_click(self.serial, MainView.SKIP.value):
            wait_click(self.serial, Confirm.SMALL.value, wait_time=0.5)

class ThirdStage(MainStageHooks):
    def on_start_page(self, base: BaseMainStage):
        if exist(self.serial, Leonard.BG_HAPPY.value, threshold=0.8):
            wait_click(self.serial, Battle.SPEED_BTN_OFF.value)

        if exist(self.serial, Leonard.BG_JUMP.value, threshold=0.8):
            wait_click(self.serial, Battle.SPEED_BTN_ON.value)

        exist_click(self.serial, Battle.SPEED_BTN_OFF.value, threshold=0.8)

class AutoStage(MainStageHooks):
    def on_start_page(self, base: BaseMainStage):
        if exist(self.serial, Leonard.BG_HAPPY.value, threshold=0.8):
            wait_click(self.serial, Battle.AUTO_BTN_ON.value)

        if exist(self.serial, Leonard.BG_JUMP.value, threshold=0.8):
            wait_click(self.serial, Battle.AUTO_BTN_OFF.value)

        exist_click(self.serial, Battle.AUTO_BTN_OFF.value, threshold=0.8)  

class FriendStage(MainStageHooks):
    def on_start_page(self, base: BaseMainStage):
        if exist(self.serial, Leonard.BG_CLAP.value, threshold=0.8):
            wait_click(self.serial, base.FRIEND)

        if exist_click(self.serial, MainView.SKIP.value):
            exist_click(self.serial, Confirm.SMALL.value)

    def on_pre_start_page_next(self, base: BaseMainStage):
        if wait_click(self.serial, MainView.SKIP.value, timeout=5.0):
            wait_click(self.serial, Confirm.SMALL.value, wait_time=1.0)
        wait_click(self.serial, MainView.SKIP.value, timeout=5.0, wait_time=1.0)
        (x, y) = get_pos(self.serial, MainStage.JAMES_FRIEND.value)
        wait_click(self.serial, (x, y - 50), wait_time=1.0)