from core.system.logger import log_msg
from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, back, drag
from scripts.shared.utils.retry import connection_retry
from scripts.shared.utils.hacks import apply_mode
from core.base.exceptions import GameError
from scripts.shared.constants import Settlement, GameView, Battle, Confirm, MainView, Leonard, Retry, Positions
from scripts.shared.events.teams.enum import TeamsImg
from scripts.shared.events.pre_stage.enum import PreStageImg
from scripts.shared.controller.context import GameContext
import time

class PreStage():
    def __init__(self, context: GameContext):
        self.ctx = context
        self.MEMBER1 = Positions.MEMBER1.value
        self.MEMBER2 = Positions.MEMBER2.value
        self.MEMBER3 = Positions.MEMBER3.value
        self.MEMBER4 = Positions.MEMBER4.value
        self.MEMBER5 = Positions.MEMBER5.value
        self.DIAMOND = Positions.DIAMOND.value
        self.MISSILE = Positions.MISSILE.value

    def on_page(self):
        has_moon_dialogue = exist(self.ctx.serial, PreStageImg.MOON_DIALOGUE.value, threshold=0.9)
        has_nickname = exist(self.ctx.serial, PreStageImg.NICKNAME_TEXT.value, threshold=0.9)
        return has_moon_dialogue or has_nickname

    def _spam_click_members(self):
        wait_click(self.ctx.serial, self.MEMBER1, wait_time=0.0)
        wait_click(self.ctx.serial, self.MEMBER2, wait_time=0.0)
        wait_click(self.ctx.serial, self.MEMBER3, wait_time=0.0)
        wait_click(self.ctx.serial, self.MEMBER4, wait_time=0.0)
        wait_click(self.ctx.serial, self.MEMBER5, wait_time=0.0)
        wait_click(self.ctx.serial, self.DIAMOND, wait_time=0.0)
        wait_click(self.ctx.serial, self.MISSILE, wait_time=1.0)

    def _handle_nickname(self):
        if exist(self.ctx.serial, PreStageImg.MOON_DIALOGUE.value, threshold=0.9):
            return

        start_time = time.time()
        while time.time() - start_time < 60:
            if exist(self.ctx.serial, Retry.TEXT1.value, threshold=0.8):
                exist_click(self.ctx.serial, Retry.BTN.value)
                continue

            if exist(self.ctx.serial, PreStageImg.NICKNAME_TEXT.value, threshold=0.9) or \
                exist(self.ctx.serial, PreStageImg.NICKNAME_COMPLETE.value, threshold=0.9):
                wait_click(self.ctx.serial, Confirm.SMALL.value)
                continue

            if exist(self.ctx.serial, PreStageImg.MOON_DIALOGUE.value, threshold=0.9):
                return
        raise GameError("設定暱稱超時")

    def _handle_battle(self):
        log_msg(self.ctx.serial, "進去前置關卡")

        if exist_click(self.ctx.serial, MainView.SKIP.value):
            wait_click(self.ctx.serial, Confirm.SMALL.value)
        
        start_time = time.time()
        
        while time.time() - start_time < 240:
            if exist(self.ctx.serial, Battle.PAUSE.value, threshold=0.8):
                self._spam_click_members()
            if exist(self.ctx.serial, Retry.TEXT1.value, threshold=0.8):
                exist_click(self.ctx.serial, Retry.BTN.value)
            if exist(self.ctx.serial, MainView.SETTINGS.value):
                return
            if exist_click(self.ctx.serial, MainView.SKIP.value):
                wait_click(self.ctx.serial, Confirm.SMALL.value)
            if exist(self.ctx.serial, GameView.ICON.value, threshold=0.9):
                break
        raise GameError("前置關卡超時")

    def run(self):
        self._handle_nickname()
        self._handle_battle()

def on_pre_stage_page(context: GameContext) -> bool:
    handler = PreStage(context)
    return handler.on_page()

def pre_stage_finish(context: GameContext):
    handler = PreStage(context)
    handler.run()