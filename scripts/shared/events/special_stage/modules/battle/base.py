import time
from scripts.shared.controller.context import GameContext
from scripts.shared.events.special_stage.session import SpecialStageSession
from scripts.shared.constants import Settlement, Retry, Battle, Leonard
from scripts.shared.events.special_stage.enum import SpecialStage
from core.actions.vision import exist, exist_click, wait_click
from core.base.exceptions import GameError

class SpecialStageBattle:
    def __init__(self, context: GameContext, session: SpecialStageSession):
        self.ctx = context
        self.session = session

    def run(self):
        timeout = 600 if self.session.is_loop_mode else 300
        start_time = time.time()

        while time.time() - start_time < timeout:
            if exist(self.ctx.serial, Retry.TEXT1.value):
                exist_click(self.ctx.serial, Retry.BTN.value)
                continue

            if self.session.is_loop_mode:
                if exist(self.ctx.serial, Battle.LOOP_END_TEXT.value):
                    return
            else:
                if exist(self.ctx.serial, Settlement.TEXT.value, threshold=0.9) or \
                   exist(self.ctx.serial, Settlement.LEVEL_UP_TEXT.value):
                    return
                
            if exist(self.ctx.serial, Leonard.TP_POINT.value):
                wait_click(self.ctx.serial, (819, 411), wait_time=1.0)

        raise GameError("特殊關卡戰鬥執行逾時")