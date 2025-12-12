import os
import time
from core.system.logger import log_msg
from core.actions.screen import (
    exist_click, wait_click, wait, wait_vanish,
    drag, back, exist
)
from scripts.shared.utils.retry import connection_retry
from core.base.exceptions import GameError
from scripts.shared.events.gacha.enum import GachaImg
from scripts.shared.events.main_stage.enum import MainStage
from scripts.shared.constants import MainView, Confirm, Leonard, Retry
from scripts.shared.controller.context import GameContext

class TutorialStrategy:
    def __init__(self, context: GameContext):
        self.ctx = context

    def proccess(self):
        if not wait(self.ctx.serial, Leonard.TP_POINT.value, timeout=2.0):
            return
        for _ in range(5):
            wait_click(self.ctx.serial, GachaImg.TEXT.value)

        wait_click(self.ctx.serial, GachaImg.GEAR_NAV.value, threshold=0.9)
        wait_click(self.ctx.serial, GachaImg.TEXT.value, threshold=0.9)
        wait_click(self.ctx.serial, (1024, 583), wait_time=1.0)

        if not exist(self.ctx.serial, GachaImg.GUARANTEE_TEXT.value, threshold=0.8):
            raise GameError("無法完成扭蛋教學")

        for _ in range(3):
            wait_click(self.ctx.serial, MainView.CLOSE_BOARD2.value, threshold=0.5)

        if not wait_click(self.ctx.serial, GachaImg.SHOP.value):
            raise GameError("無法關閉扭蛋教學")
        
        if not wait_click(self.ctx.serial, Leonard.TP_GIFT.value, threshold=0.9):
            raise GameError("無法關閉扭蛋教學")

        wait_click(self.ctx.serial, MainView.BACK.value)
        wait_click(self.ctx.serial, Leonard.TP_HAPPY.value)