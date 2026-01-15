from scripts.shared.controller.context import GameContext
from scripts.shared.events.special_stage.session import SpecialStageSession
from scripts.shared.events.special_stage.enum import SpecialStage
from scripts.shared.constants import MainView, Retry, Battle
from scripts.shared.utils.retry import connection_retry
from core.actions.vision import wait_click, exist, drag, exist_click
from core.base.exceptions import GameError
import time

class SpecialStageNavUtils:
    def __init__(self, context: GameContext, session: SpecialStageSession):
        self.ctx = context
        self.session = session

    def _handle_pre_anime(self):
        start_time = time.time()
        while time.time() - start_time < 80:
            if exist(self.ctx.serial, SpecialStage.TEXT.value):
                break
            exist_click(self.ctx.serial, Battle.ANIME.value, wait_time=1.5)

    def _leave(self, back: bool = False):
        start_time = time.time()
        while time.time() - start_time < 60:
            if exist(self.ctx.serial, Retry.TEXT1.value, threshold=0.9) or exist(self.ctx.serial, Retry.TEXT2.value, threshold=0.9):
                wait_click(self.ctx.serial, Retry.BTN.value)
                continue
            
            if exist(self.ctx.serial, Battle.NEXT.value, threshold=0.9):
                wait_click(self.ctx.serial, MainView.BACK.value, wait_time=1.0)
                cnt = 0
                continue

            if exist(self.ctx.serial, Battle.START.value, threshold=0.9):
                wait_click(self.ctx.serial, MainView.BACK.value, wait_time=1.0)
                cnt = 0
                continue

            if exist(self.ctx.serial, SpecialStage.ENTER.value, threshold=0.9):
                wait_click(self.ctx.serial, MainView.BACK.value, wait_time=1.0)
                cnt = 0
                continue

            
            if exist(self.ctx.serial, SpecialStage.LAB.value, threshold=0.9):
                if back:
                    wait_click(self.ctx.serial, MainView.BACK.value, wait_time=1.0)
                    cnt = 0
                    continue
                else:
                    return

            cnt += 1
            if cnt >= 2:
                return
            else:
                time.sleep(1.0)
            
        raise GameError("無法離開準備畫面")