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
from typing import List
from scripts.shared.controller.context import GameContext
from scripts.shared.utils.mainview.enum import MainViewState
from scripts.shared.events.main_stage.enum import MainStage
from scripts.shared.events.special_stage.enum import SpecialStage
from scripts.shared.events.seven_days.enum import SevenDaysImg
from scripts.shared.events.special_quest.enum import SpecialQuestImg
from scripts.shared.events.gacha.enum import GachaImg
from scripts.shared.events.teams.enum import TeamsImg

class DimmedStrategy():
    """
    brightness is too low
    """
    def __init__(self, ctx: GameContext):
        self.ctx = ctx

        self.regions: dict[MainViewState, tuple[int, int, int, int] | None] = {
            MainViewState.MAIN_STAGE: None,
            MainViewState.SPECIAL_STAGE: None,
            MainViewState.SEVEN_DAYS: None,
            MainViewState.SPECIAL_QUEST: None,
            MainViewState.TEAM: None,
            MainViewState.UPGRADE: None,
            MainViewState.GACHA: (798, 79, 971, 237),
        }

        self.image_mapping = {
            MainViewState.MAIN_STAGE: MainStage.BTN.value,
            MainViewState.SPECIAL_STAGE: SpecialStage.BTN.value,
            MainViewState.SEVEN_DAYS: SevenDaysImg.BTN.value,
            MainViewState.SPECIAL_QUEST: SpecialQuestImg.BTN.value,
            MainViewState.TEAM: TeamsImg.BTN.value,
            MainViewState.UPGRADE: [TeamsImg.RENE_MAINVIEW.value, TeamsImg.SHEEP_MAINVIEW.value],
        }

    def initalize_regions(self):
        for state, imgs in self.image_mapping.items():
            if self.regions[state] is None:
                if isinstance(imgs, list):
                    for img in imgs:
                        loc = get_pos(self.ctx.serial, img, threshold=0.8, return_center=False)
                        if loc:
                            self.regions[state] = loc
                            break
                else:
                    loc = get_pos(self.ctx.serial, imgs, threshold=0.8, return_center=False)
                    if loc:
                        self.regions[state] = loc

    def handle_supported(self) -> bool:
        if exist(self.ctx.serial, MainView.CLOSE_PVP.value, threshold=0.9): # change to detect text for better accuracy
            wait_click(self.ctx.serial, MainView.CLOSE_PVP.value)
            return True
        
        if exist(self.ctx.serial, MainView.POLICY_TEXT.value, threshold=0.99):
            wait_click(self.ctx.serial, Confirm.CANCEL.value)
            return True
        
        if exist(self.ctx.serial, SeasonPassImg.POP_DETAIL_TEXT.value, threshold=0.99):
            wait_click(self.ctx.serial, MainView.CLOSE_BOARD2.value)
            return True
       
        if exist_click(self.ctx.serial, MainView.SKIP.value, threshold=0.85):
            if exist(self.ctx.serial, MainView.SKIP_TUTORIAL_TEXT.value, threshold=0.9):
                wait_click(self.ctx.serial, Confirm.SMALL.value)
            return True

        if exist_click(self.ctx.serial, MainView.SKIP_2.value, threshold=0.9):
            return True
        return False
    
    def handle_event(self) -> MainViewState:
        if exist(self.ctx.serial, MainView.TO_DOWNLOAD_TEXT.value, threshold=0.9):
            return MainViewState.TO_DOWNLOAD

        u = find_spotlight_center(self.ctx.serial)
        if u is None:
            return MainViewState.UNKNOWN

        midx, midy = u
        for state, region in self.regions.items():
            if region is not None:
                x1, y1, x2, y2 = region
                if x1 <= midx <= x2 and y1 <= midy <= y2:
                    return state

        return MainViewState.UNKNOWN