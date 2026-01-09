import os
import time
from core.system.logging.logger import log_msg
from core.actions.vision import (
    exist_click, wait_click, wait, wait_vanish,
    drag, back, exist, get_pos,
    check_region_brightness
)
from core.actions.system import pull_account_file
from core.actions.vision import match_string_from_region
from scripts.shared.events.gacha.config import GachaSession
from scripts.shared.utils.retry import connection_retry
from core.base.exceptions import GameError
from scripts.shared.events.gacha.enum import GachaImg
from scripts.shared.constants import MainView, Confirm, Leonard
from scripts.shared.controller.context import GameContext
from scripts.shared.events.gacha.interrupts.tutorial import TutorialStrategy
from scripts.shared.events.gacha.interrupts.jessica import JessicaStrategy
from scripts.shared.events.gacha.interrupts.shirt import ShirtStrategy

class GachaNavigator:
    def __init__(self, context: GameContext, session: GachaSession):
        self.ctx = context
        self.session = session

        self.tutorial_strategy = TutorialStrategy(context)
        self.jessica_strategy = JessicaStrategy(context)
        self.shirt_strategy = ShirtStrategy(context)

    def on_interrupt(self):
        loc = get_pos(self.ctx.serial, GachaImg.TEXT.value, threshold=0.8, return_center=False)
        if loc:
            if check_region_brightness(self.ctx.serial, region=loc, threshold=45):
                return False
        return True

    def enter_menu(self):
        if not exist(self.ctx.serial, GachaImg.TEXT.value):
            if not wait_click(self.ctx.serial, GachaImg.BTN.value):
                raise GameError("無法進入扭蛋選單")
            connection_retry(self.ctx.serial, vanish=GachaImg.BTN.value, retry=GachaImg.BTN.value, timeout=80.0)

        if self.session.on_event:
            log_msg(self.ctx.serial, "偵測到扭蛋活動，進入活動流程")
            self._on_event()
        else:
            self.tutorial_strategy.proccess()
            if self.on_interrupt():
                raise GameError("無法完成扭蛋教學")

    def leave_menu(self):
        if not wait_click(self.ctx.serial, MainView.BACK.value):
            raise GameError("無法離開扭蛋選單")
        connection_retry(self.ctx.serial, vanish=GachaImg.TEXT.value, timeout=40.0)

    def _on_event(self):
        if wait(self.ctx.serial, Leonard.DIALOGUE_TAG.value, threshold=0.9):
            exist_click(self.ctx.serial, MainView.SKIP.value)
            if wait(self.ctx.serial, MainView.SKIP_CONFIRM_TEXT.value, threshold=0.9, timeout=3.0):
                wait_click(self.ctx.serial, Confirm.SMALL.value)
            if wait(self.ctx.serial, GachaImg.JESSICA_POOL_TEXT.value, threshold=0.9):
                self.jessica_strategy.proccess()
            else:
                self.shirt_strategy.proccess()
            log_msg(self.ctx.serial, "完成扭蛋活動流程")
        else:
            raise GameError("無法完成扭蛋活動")
