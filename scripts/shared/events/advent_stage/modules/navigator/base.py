from scripts.shared.controller.context import GameContext
from core.actions.vision import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos, check_region_brightness
from scripts.shared.events.advent_stage.modules.navigator.utils import StageNavigatorUtils
from scripts.shared.utils.retry import connection_retry
from scripts.shared.constants import Settlement, Confirm, Battle, MainView, Retry, Positions
from core.base.exceptions import GameError
from core.system.logging.logger import log_msg
from scripts.shared.events.advent_stage.enum import AdventImg, AdventStageName
from typing import Optional, Tuple
from scripts.shared.events.main_stage.enum import MainStageImg
from core.system.config import Config
from scripts.shared.constants import Leonard
from scripts.shared.events.advent_stage.modules.interrupt.tutorial import TutorialInterrupt 
from scripts.shared.events.advent_stage.session import AdventStageSession
import time

class StageNavigator:
    def __init__(self, context: GameContext, session: AdventStageSession):
        self.ctx = context
        self.session = session

        self.tutorial_interrupt = TutorialInterrupt(self.ctx)
        self.utils = StageNavigatorUtils(context)
    
    def on_interrupt(self):
        loc = get_pos(self.ctx.serial, AdventImg.TEXT.value, threshold=0.9, return_center=False)
        if loc is None:
            return False
        if check_region_brightness(self.ctx.serial, loc, threshold=45):
            return False
        return True

    def enter_menu(self):
        self.utils._attempt_enter()
        self.utils._handle_pre_anime()

    def leave_menu(self):
        wait_click(self.ctx.serial, MainView.BACK.value)
        connection_retry(self.ctx.serial, vanish=[(AdventImg.TEXT.value, 0.9)], timeout=40.0)

    def handle_interrupt(self):
        start_time = time.time()    
        cnt = 0
        while time.time() - start_time < 60.0:
            if not self.on_interrupt():
                cnt += 1
                if cnt >= 2:
                    return False
                else:
                    time.sleep(1.0)
            elif self.tutorial_interrupt.handle():
                continue
        raise GameError("降臨關卡 interrupt 處理超時")

    def handle_menu_page(self):
        self.handle_interrupt()

        if self.session.on_event:
            self.leave_menu()
            return True