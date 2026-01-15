import time
from typing import Tuple, Optional
from scripts.shared.controller.context import GameContext
from scripts.shared.events.special_stage.session import SpecialStageSession
from scripts.shared.events.main_stage.enum import MainStageImg
from scripts.shared.events.special_stage.enum import SpecialStage, Planet
from scripts.shared.constants import Confirm, MainView, Retry
from scripts.shared.utils.retry import connection_retry
from core.actions.vision import wait_click, exist_click, exist, wait, drag, get_pos
from core.base.exceptions import GameError

class SpecialStageFinder:
    REGIONS = {
        Planet.EVO_MINE: (176, 175, 188, 101),
        # Planet.WIZARD_CUBE: (176, 165, 172, 98),
        # Planet.IMMORTAL_SKULL: (176, 165, 172, 98),
        # Planet.LIBRARY: (176, 188, 188, 101),
        # Planet.COLLAB: (188, 180, 180, 105),
        # Planet.LEONARD: (188, 180, 180, 105),
        # Planet.CHRISTMAS: (188, 180, 180, 105),
    }

    def __init__(self, context: GameContext, session: SpecialStageSession):
        self.ctx = context
        self.session = session

    def _find_planet_region(self) -> Tuple[int, int, int, int]:
        planet = self.session.planet
        for _ in range(3):
            drag(self.ctx.serial, (75, 392), (600, 392), wait_time=0.3)

        for _ in range(10):
            pos = get_pos(self.ctx.serial, planet)
            if pos:
                x, y = pos
                drag(self.ctx.serial, (x, y), (480, y), wait_time=1.5)
                
                final_pos = get_pos(self.ctx.serial, planet)
                if final_pos:
                    fx, fy = final_pos
                    crop = self.REGIONS.get(planet)
                    return (fx - crop[0], fy - crop[1], fx + crop[2], fy + crop[3])
                break
            
            drag(self.ctx.serial, (450, 392), (150, 392), duration=800, wait_time=1.5)
        
        raise GameError("無法定位星球位置")
    
    def enter_stage_menu(self, region: Tuple[int, int, int, int]):
        if not wait_click(self.ctx.serial, SpecialStage.STAGE(stage=self.session.stage_num), region=region, threshold=0.8):
            return False
        connection_retry(self.ctx.serial, appear=[(SpecialStage.ENTER.value)], timeout=40.0)
        return True

    def enter_preperation_page(self):
        wait_click(self.ctx.serial, SpecialStage.ENTER.value)

        start_time = time.time()
        while time.time() - start_time < 50:
            if exist(self.ctx.serial, Retry.TEXT1.value):
                exist_click(self.ctx.serial, Retry.BTN.value)
                continue

            if exist(self.ctx.serial, SpecialStage.LIMITED.value):
                exist_click(self.ctx.serial, Confirm.SMALL.value, wait_time=1.0)
                self.session.stage_stop = True
                continue
            
            if self.session.stage_stop:
                if exist_click(self.ctx.serial, MainView.BACK.value, wait_time=1.0):
                    continue
                if exist(self.ctx.serial, SpecialStage.LAB.value):
                    return
            else:
                if exist_click(self.ctx.serial, SpecialStage.ENTER.value, wait_time=1.0):
                    continue

                if exist(self.ctx.serial, MainStageImg.PREPERATION_PAGE_BG_HIGH.value):
                    return
        raise GameError("無法進入戰前準備頁面")
            
    def enter_stage(self):
        region = self._find_planet_region()
        if not self.enter_stage_menu(region):
            self.session.stage_stop = True
            return
        self.enter_preperation_page()