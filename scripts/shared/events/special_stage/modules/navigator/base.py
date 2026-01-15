from scripts.shared.controller.context import GameContext
from scripts.shared.events.special_stage.session import SpecialStageSession
from scripts.shared.events.special_stage.enum import SpecialStage
from scripts.shared.constants import MainView, Retry, Battle
from scripts.shared.utils.retry import connection_retry
from core.actions.vision import wait_click, exist, drag, exist_click
from core.base.exceptions import GameError
from scripts.shared.events.special_stage.modules.navigator.utils import SpecialStageNavUtils
import time

class SpecialStageNavigator:
    def __init__(self, context: GameContext, session: SpecialStageSession):
        self.ctx = context
        self.session = session

        self.utils = SpecialStageNavUtils(self.ctx, self.session)

    def enter_menu(self):
        if exist(self.ctx.serial, SpecialStage.TEXT.value):
            return
        
        for _ in range(5):
            if wait_click(self.ctx.serial, SpecialStage.BTN.value):
                connection_retry(self.ctx.serial, vanish=[(SpecialStage.BTN.value)], retry=[(SpecialStage.BTN.value)])
                self.utils._handle_pre_anime()
                return
            else:
                drag(self.ctx.serial, (800, 400), (200, 400), duration=500, wait_time=2.5)
        
        raise GameError("無法進入特殊關卡選單")

    def leave_menu(self):
        self.utils._leave(back=True)

    def leave_stage(self):
        self.utils._leave(back=False)

    def handle_menu_page(self) -> bool:
        if self.session.on_event:
            return True
        
        self.leave_stage()

        self.session.stage_stop = False

        if self.session.conquer_mode:
            if self.session.stage_complete:
                self.session.stage_num += 1
                self.session.stage_complete = False

            if self.session.stage_num > 6:
                return True
            return False
        
        if self.session.stage_complete:
            return True

        return False