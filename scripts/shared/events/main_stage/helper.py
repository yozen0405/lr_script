import time
from core.system.logger import log_msg
from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos, check_region_brightness
from core.actions.ocr import get_main_stage_num
from core.base.exceptions import GameError
from scripts.shared.constants.positions import Positions
from scripts.shared.utils.retry import connection_retry
from typing import Optional
from scripts.shared.constants import Settlement, Battle, Confirm, MainView, Leonard, Retry
from scripts.shared.events.main_stage.enum import MainStage, Stages, Treasure

class MainStageHelper:
    def __init__(self, serial):
        self.serial = serial

    def on_page(self):
        return exist(self.serial, MainStage.TEXT.value, threshold=0.9)

    def is_clear(self):
        loc = get_pos(self.serial, MainStage.TEXT.value, threshold=0.9, return_center=False)
        if loc is None:
            return False
        if check_region_brightness(self.serial, loc, threshold=45):
            return True
        return False

    def handle_treasure(self) -> bool:
        if not exist(self.serial, Leonard.DIALOGUE_TAG.value, threshold=0.9):
            return False
        wait_click(self.serial, Treasure.ICON.value)
        connection_retry(self.serial, appear=[(Treasure.TEXT.value, 0.9)], timeout=30.0)
        wait_click(self.serial, MainView.SKIP.value)
        wait_click(self.serial, Confirm.SMALL.value)
        wait_click(self.serial, MainView.BACK.value)
        connection_retry(self.serial, vanish=[(Treasure.TEXT.value, 0.9)], timeout=30.0)
        return True