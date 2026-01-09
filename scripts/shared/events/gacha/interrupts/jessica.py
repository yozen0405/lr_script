import os
import time
from core.system.logging.logger import log_msg
from core.actions.vision import (
    exist_click, wait_click, wait, wait_vanish,
    drag, back, exist
)
from scripts.shared.utils.retry import connection_retry
from core.base.exceptions import GameError
from scripts.shared.events.gacha.enum import GachaImg
from scripts.shared.events.main_stage.enum import MainStageImg
from scripts.shared.constants import MainView, Confirm, Leonard, Retry
from scripts.shared.controller.context import GameContext

class JessicaStrategy:
    def __init__(self, context: GameContext):
        self.ctx = context

    def _handle_pull(self):
        start_time = time.time()
        fg = False
        while time.time() - start_time < 300.0:
            if exist(self.ctx.serial, Retry.TEXT1.value) or exist(self.ctx.serial, Retry.TEXT2.value):
                exist_click(self.ctx.serial, Retry.BTN.value)
                continue

            if not fg and exist_click(self.ctx.serial, GachaImg.JESSICA_PULL_BTN.value):
                continue

            if fg and exist(self.ctx.serial, GachaImg.TEXT.value, threshold=0.8):
                return

            if exist_click(self.ctx.serial, GachaImg.SKIP.value):
                continue

            if exist(self.ctx.serial, GachaImg.SUCCESS_TEXT.value, threshold=0.9):
                fg = True
                wait_click(self.ctx.serial, GachaImg.CONFIRM.value)
                continue
        raise GameError("抽取傑西卡超時")


    def proccess(self):
        self._handle_pull()
        time.sleep(1.0)
        wait_click(self.ctx.serial, MainView.SKIP.value)
        wait_click(self.ctx.serial, Confirm.SMALL.value)
        connection_retry(self.ctx.serial, vanish=[(GachaImg.TEXT.value, 0.8)], timeout=50.0)