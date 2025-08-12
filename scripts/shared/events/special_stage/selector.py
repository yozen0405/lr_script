from scripts.shared.events.special_stage.base import BaseSpecialStage
from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from scripts.shared.utils.retry import connection_retry
from core.base.exceptions import GameError
from typing import Optional
from core.system.logger import log_msg
from scripts.shared.events.special_stage.enum import Planet

class SpecialStageTask:
    def __init__(self, serial):
        self.serial = serial
        self.base = BaseSpecialStage(serial)

    def _stage_to_region_map(self, planet: str) -> tuple[int, int, int, int]:
        stage_region_map = {
            Planet.EVO_MINE: (235, 250, 250, 135),
            Planet.WIZARD_CUBE: (235, 220, 230, 130),
            Planet.IMMORTAL_SKULL: (235, 220, 230, 130),
            Planet.LIBRARY: (235, 250, 250, 135),
            Planet.COLLAB: (240, 240, 260, 140),
            Planet.LEONARD: (250, 240, 240, 140),
        }

        if planet not in stage_region_map:
            raise ValueError(f"未知的 planet 名稱: {planet}")

        return stage_region_map[planet]
    
    def single_battle(self, planet: str, stage: int):
        self.base.enter_menu()
        crop_region = self._stage_to_region_map(planet=planet)
        region = self.base.find_target_planet(planet=planet, crop_region=crop_region)

        if self.base.enter_stage(stage_num=stage, region=region) == False:
            log_msg(self.serial, f"第{stage}關已經達到上限")
            return
        else:
            log_msg(self.serial, f"進入第{stage}關")
        self.base.single_mode_run()

    def _loop_battle(self, planet: str, stage: int, region):
        if self.base.enter_stage(stage_num=stage, region=region) == False:
            log_msg(self.serial, f"第{stage}關已經達到上限")
            return
        self.base.loop_mode_run()
    
    def loop_battle(self, planet: str, stage: int):
        self.base.enter_menu()
        crop_region = self._stage_to_region_map(planet=planet)
        region = self.base.find_target_planet(planet=planet, crop_region=crop_region)

        self._loop_battle(planet=planet, stage=stage, region=region)

    def conquer_planet(self, planet: str):
        for stage in range(1, 7):
            self.loop_battle(planet=planet, stage=stage)

def special_stage_single_game(serial, planet: str, stage: int):
    spc = SpecialStageTask(serial)
    spc.single_battle(planet=planet, stage=stage)

def special_stage_loop_game(serial, planet: str, stage: int):
    spc = SpecialStageTask(serial)
    spc.loop_battle(planet=planet, stage=stage)

def special_stage_conquer_planet(serial, planet: str):
    spc = SpecialStageTask(serial)
    spc.conquer_planet(planet=planet)