import time
from core.system.logging.logger import log_msg
from core.actions.vision import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from core.actions.vision import get_main_stage_num
from core.base.exceptions import GameError
from scripts.shared.constants.positions import Positions
from scripts.shared.events.main_stage.modules.preperation.utils import PreperationUtils
from scripts.shared.utils.retry import connection_retry
from typing import Optional
from scripts.shared.constants import Settlement, Battle, Confirm, MainView, Leonard, Retry
from scripts.shared.events.main_stage.enum import MainStageImg, Stages, Treasure
from scripts.shared.controller.context import GameContext
from scripts.shared.events.main_stage.session import StageSession
from scripts.shared.events.main_stage.modules.preperation.interrupt.mutipiler_tutorial import MultiplierTutorialInterrupt
from scripts.shared.utils.hacks import apply_mode

class PreparationBase:
    def __init__(self, context: GameContext, session: StageSession):
        self.ctx = context
        self.session = session

        self.utils = PreperationUtils(context, session)

    def on_interrupt(self) -> bool:
        return self.utils.on_interrupt()

    def enter_stage(self):
        start_time = time.time()
        while time.time() - start_time < 60.0:
            if exist(self.ctx.serial, MainStageImg.PREPERATION_PAGE_BG_LOW.value, threshold=0.9):
                self.utils.configure_current_stage()
                return
            
            if exist(self.ctx.serial, MainStageImg.PREPERATION_PAGE_BG_HIGH.value, threshold=0.9):
                self.utils.configure_current_stage()
                return
            
            if exist_click(self.ctx.serial, Battle.ANIME.value, wait_time=1.8):
                continue
        raise GameError("未知的主要關卡")
    
    def run(self):
        self.utils.configure_battle_settings()

        start_time = time.time()
        pressed_start = False
        cnt = 0
        while time.time() - start_time < 120.0:
            if exist(self.ctx.serial, Retry.TEXT1.value, threshold=0.9) or exist(self.ctx.serial, Retry.TEXT2.value, threshold=0.9):
                wait_click(self.ctx.serial, Retry.BTN.value)
                continue

            if exist(self.ctx.serial, Battle.START.value, threshold=0.9):
                exist_click(self.ctx.serial, Battle.START.value)
                pressed_start = True
                cnt = 0
            elif exist(self.ctx.serial, Battle.NEXT.value, threshold=0.8):
                exist_click(self.ctx.serial, Battle.NEXT.value)
                cnt = 0
            elif pressed_start:
                cnt += 1
                if cnt >= 2:
                    return
                if exist(self.ctx.serial, Battle.PAUSE.value):
                    return

            if self.session.is_first:
                self.session.stage_cls.on_preperation_start()
        raise GameError("無法進入戰鬥準備頁面")