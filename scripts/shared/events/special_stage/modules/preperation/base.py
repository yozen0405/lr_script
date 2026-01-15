from scripts.shared.controller.context import GameContext
from scripts.shared.events.special_stage.session import SpecialStageSession
from scripts.shared.events.special_stage.enum import SpecialStage
from scripts.shared.events.main_stage.enum import MainStageImg
from scripts.shared.constants import Battle, Confirm, Retry, MainView
from core.actions.vision import wait_click, exist_click, exist, wait
from core.base.exceptions import GameError
from scripts.shared.events.special_stage.modules.preperation.utils import SpecialStagePrepUtils
import time

class SpecialStagePreperation:
    def __init__(self, context: GameContext, session: SpecialStageSession):
        self.ctx = context
        self.session = session
        self.utils = SpecialStagePrepUtils(self.ctx, self.session)

    def run(self):
        self.utils.configure_battle_settings()

        start_time = time.time()
        pressed_start = False
        cnt = 0
        while time.time() - start_time < 120.0:
            if exist(self.ctx.serial, Retry.TEXT1.value, threshold=0.9) or exist(self.ctx.serial, Retry.TEXT2.value, threshold=0.9):
                wait_click(self.ctx.serial, Retry.BTN.value)
                continue

            if exist_click(self.ctx.serial, Battle.START.value, threshold=0.9, wait_time=1.0):
                pressed_start = True
                cnt = 0
            elif exist_click(self.ctx.serial, Battle.NEXT.value, threshold=0.8, wait_time=1.0):
                cnt = 0
            elif pressed_start:
                cnt += 1
                if cnt >= 2:
                    return
                if exist(self.ctx.serial, Battle.PAUSE.value):
                    return

        raise GameError("無法進入戰鬥準備頁面")