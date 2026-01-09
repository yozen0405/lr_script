import time
from core.system.logging.logger import log_msg
from core.actions.vision import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos, check_region_brightness
from core.base.exceptions import GameError
from scripts.shared.constants.positions import Positions
from scripts.shared.controller.context import GameContext
from scripts.shared.events.main_stage.session import StageSession
from scripts.shared.utils.retry import connection_retry
from typing import Optional
from scripts.shared.constants import Settlement, Battle, Confirm, MainView, Leonard, Retry
from scripts.shared.events.main_stage.enum import MainStageImg, Stages, Treasure

class TreasureBase:
    def __init__(self, context: GameContext, session: StageSession):
        self.ctx = context
        self.session = session

    def on_page(self):
        return exist(self.ctx.serial, Treasure.TEXT.value, threshold=0.9)
    
    def enter_menu(self):
        wait_click(self.ctx.serial, Treasure.ICON.value)
        connection_retry(self.ctx.serial, appear=[(Treasure.TEXT.value, 0.9)], timeout=30.0)

    def handle_event(self) -> bool:
        if not exist(self.ctx.serial, Leonard.DIALOGUE_TAG.value, threshold=0.9):
            return False
        self.enter_menu()
        wait_click(self.ctx.serial, MainView.SKIP.value)
        wait_click(self.ctx.serial, Confirm.SMALL.value)
        wait_click(self.ctx.serial, MainView.BACK.value)
        connection_retry(self.ctx.serial, vanish=[(Treasure.TEXT.value, 0.9)], timeout=30.0)
        return True