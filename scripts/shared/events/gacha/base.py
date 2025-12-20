import os
import time
from core.system.logger import log_msg
from core.actions.screen import (
    exist_click, wait_click, wait, wait_vanish,
    drag, back, exist, get_pos,
    check_region_brightness
)
from core.actions.system import get_clipboard_text
from core.actions.system import pull_account_file
from core.actions.ocr import match_string_from_region
from scripts.shared.utils.retry import connection_retry
from core.base.exceptions import GameError
from scripts.shared.events.gacha.enum import GachaImg
from scripts.shared.constants import MainView, Confirm, Leonard
from scripts.shared.controller.context import GameContext
from scripts.shared.events.gacha.interrupts.tutorial import TutorialStrategy
from scripts.shared.events.gacha.interrupts.jessica import JessicaStrategy
from scripts.shared.events.gacha.modules.ranger import PullRangerModule
from scripts.shared.events.gacha.interrupts.shirt import ShirtStrategy

class BaseGacha:
    def __init__(self, context: GameContext):
        self.ctx = context
        self.serial = context.serial

        self.tutorial_strategy = TutorialStrategy(context)
        self.jessica_strategy = JessicaStrategy(context)
        self.shirt_strategy = ShirtStrategy(context)
        self.pull_ranger_module = PullRangerModule(context)
        
    def on_interrupt(self):
        loc = get_pos(self.ctx.serial, GachaImg.TEXT.value, threshold=0.8, return_center=False)
        if loc:
            if check_region_brightness(self.ctx.serial, region=loc, threshold=45):
                return False
        return True

    def _enter_menu(self):
        if not exist(self.serial, GachaImg.TEXT.value):
            if not wait_click(self.serial, GachaImg.BTN.value):
                raise GameError("無法進入扭蛋選單")
            connection_retry(self.serial, vanish=GachaImg.BTN.value, retry=GachaImg.BTN.value, timeout=40.0)
    
    def _on_pre_tutorial(self):
        self.tutorial_strategy.proccess()
        if self.on_interrupt():
            raise GameError("無法完成扭蛋教學")

    def enter_menu(self):
        self._enter_menu()
        self._on_pre_tutorial()

    def leave_menu(self):
        if not wait_click(self.serial, MainView.BACK.value):
            raise GameError("無法離開扭蛋選單")
        connection_retry(self.serial, vanish=GachaImg.TEXT.value, timeout=40.0)

    def on_event(self):
        self._enter_menu()
        if exist(self.ctx.serial, Leonard.DIALOGUE_TAG.value, threshold=0.9):
            exist_click(self.ctx.serial, MainView.SKIP.value)
            if exist(self.ctx.serial, MainView.SKIP_TUTORIAL_TEXT.value, threshold=0.9):
                wait_click(self.ctx.serial, Confirm.SMALL.value)
                self.shirt_strategy.proccess()
            else:
                if wait(self.ctx.serial, GachaImg.JESSICA_POOL_TEXT.value, threshold=0.9):
                    self.jessica_strategy.proccess()

    def pull_ranger(self, attempts: int = 15):
        self.enter_menu()
        self.pull_ranger_module.pull(attempts)
        self.leave_menu()

def pull_ranger(context: GameContext, attempts: int = 15):
    gacha = BaseGacha(context)
    gacha.pull_ranger(attempts)

def on_gacha_event(context: GameContext):
    gacha = BaseGacha(context)
    gacha.on_event()