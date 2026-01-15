import time
from scripts.shared.controller.context import GameContext
from scripts.shared.events.special_stage.session import SpecialStageSession
from scripts.shared.constants import Settlement, Confirm, Retry, MainView, Battle
from scripts.shared.events.special_stage.enum import SpecialStage
from core.actions.vision import exist, exist_click, wait_click
from core.base.exceptions import GameError

class SpecialStageSettlement:
    def __init__(self, context: GameContext, session: SpecialStageSession):
        self.ctx = context
        self.session = session

    def handle_items(self):
        click_targets = [
            Confirm.BIG1.value, 
            Confirm.BIG2.value, 
            Settlement.ONE_REWARD.value, 
            Confirm.SMALL.value, 
            Settlement.STOP.value, 
            Settlement.SILVER_BOX.value, 
            Settlement.BRONZE_BOX.value, 
            Settlement.TEXT.value
        ]
        
        for img in click_targets:
            exist_click(self.ctx.serial, img, wait_time=1.0)
            continue

    def run(self):
        start_time = time.time()
        self.session.stage_complete = True
        while time.time() - start_time < 120:
            if exist(self.ctx.serial, Retry.TEXT1.value):
                exist_click(self.ctx.serial, Retry.BTN.value)

            if exist(self.ctx.serial, SpecialStage.TEXT.value):
                return

            if self.session.is_loop_mode:
                if exist(self.ctx.serial, Battle.LOOP_END_TEXT.value):
                    wait_click(self.ctx.serial, Confirm.BIG3.value, wait_time=1.0)
            else:
                self.handle_items()

        raise GameError("特殊館卡結算流程逾時")