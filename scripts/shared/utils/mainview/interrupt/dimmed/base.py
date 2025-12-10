import time
import os
from core.system.logger import log_msg
from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, back, drag, find_spotlight_center
from core.base.exceptions import GameError
from scripts.shared.constants import MainView, Confirm, Retry
import time
from abc import ABC, abstractmethod
from enum import Enum, auto
from core.actions.screen import wait_click, exist_click, exist, wait, get_pos, check_region_brightness
from core.base.exceptions import GameError
from scripts.shared.events.season_pass.enum import SeasonPassImg
from scripts.shared.constants import MainView
from scripts.shared.utils.mainview.interrupt.base import BaseStrategy
from typing import List
from scripts.shared.utils.mainview.interrupt.dimmed.events.close_board_rare.base import CloseBoardRareStrategy
from scripts.shared.utils.mainview.interrupt.dimmed.events.close_board_general.base import CloseBoardGeneralStrategy
from scripts.shared.utils.mainview.interrupt.dimmed.events.tutorials.base import TutorialStrategy

class DimmedStrategy(BaseStrategy):
    """
    brightness is too low
    """
    def __init__(self, serial):
        self.serial = serial

        self.strategies: List[BaseStrategy] = {
            CloseBoardRareStrategy(serial),
            CloseBoardGeneralStrategy(serial),
            TutorialStrategy(serial),
        }

    def check(self) -> bool:
        return True
    
    def proccess(self):
        for strategy in self.strategies:
            if strategy.check():
                strategy.proccess()
                return
        self._handle_guide_arrow()

    def _handle_guide_arrow(self) -> bool:
        loc = find_spotlight_center(self.serial)
        wait_click(self.serial, loc)
        return True