from core.actions.vision import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos, check_region_brightness
from core.actions.vision import back
from scripts.shared.utils.retry import connection_retry
from scripts.shared.constants import Settlement, Confirm, Battle, MainView, Retry, Positions
from core.base.exceptions import GameError
from core.system.logging.logger import log_msg
from typing import List, Optional, Tuple
from scripts.shared.events.teams.enum import TeamsImg
from scripts.shared.constants.leonard import Leonard
from scripts.shared.controller.context import GameContext
import time

class RangerFilterPage():
    def __init__(self, context: GameContext):
        self.ctx = context

    def on_page(self) -> bool:
        return exist(self.ctx.serial, TeamsImg.FILTER_BTN.value, threshold=0.9)

    def filter(self, 
               filter_list: Optional[List[TeamsImg]] = [TeamsImg.FILTER_EIGHT_STARS, TeamsImg.FILTER_RANGER],
                sort: TeamsImg = TeamsImg.LVL_ASC
               ):
        wait_click(self.ctx.serial, TeamsImg.FILTER_BTN.value, wait_time=0.0)
        if not wait_click(self.ctx.serial, TeamsImg.RESET.value, wait_time=0.0):
            raise GameError("Cannot reset filter in teams page.")
        
        for img in filter_list:
            wait_click(self.ctx.serial, img.value, wait_time=0.0)

        wait_click(self.ctx.serial, Confirm.SMALL.value, wait_time=0.2)
        wait_click(self.ctx.serial, TeamsImg.SORT_BY_BTN.value, wait_time=0.0)

        for _ in range(2):
            exist_click(self.ctx.serial, sort.value, wait_time=0.0)

    def reset(self):
        self.filter(filter_list=[], sort=TeamsImg.SORT_LATEST)