from typing import Optional, List, Union
from scripts.shared.controller.context import GameContext
from scripts.shared.utils.mainview.enum import MainViewState
from scripts.shared.events.main_stage.enum import MainStageImg
from scripts.shared.events.seven_days.enum import SevenDaysImg
from scripts.shared.events.special_quest.enum import SpecialQuestImg
from scripts.shared.events.teams.enum import TeamsImg
from scripts.shared.events.gacha.enum import GachaImg
from scripts.shared.events.special_stage.enum import SpecialStage
from core.actions.vision import get_pos, check_region_brightness

class EventDetector:
    def __init__(self, ctx: GameContext):
        self.ctx = ctx
        self.serial = ctx.serial

    def detect_active_state(self) -> MainViewState:
        check_list = [
            (MainViewState.MAIN_STAGE, [MainStageImg.BTN.value]),
            (MainViewState.SEVEN_DAYS, [SevenDaysImg.BTN.value]),
            (MainViewState.SPECIAL_QUEST, [SpecialQuestImg.BTN.value]),
            (MainViewState.TEAM, [TeamsImg.BTN.value]),
            (MainViewState.UPGRADE, [TeamsImg.RENE_MAINVIEW.value, TeamsImg.SHEEP_MAINVIEW.value]),
            (MainViewState.GACHA, [GachaImg.BTN.value]),
        ]

        for state, images in check_list:
            if self._is_any_highlighted(images):
                return state

        return MainViewState.UNKNOWN

    def is_special_stage_active(self) -> bool:
        return self._is_any_highlighted([SpecialStage.BTN.value])

    def _is_any_highlighted(self, images: List[str]) -> bool:
        for img in images:
            loc = get_pos(self.serial, img, threshold=0.9, return_center=False)
            
            if not loc:
                continue
            
            if check_region_brightness(self.serial, region=loc, threshold=50):
                return True
                
        return False