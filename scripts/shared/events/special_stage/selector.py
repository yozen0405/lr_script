from scripts.shared.events.special_stage.base import BaseSpecialStage
from core.actions.actions import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from scripts.shared.utils.retry import connection_retry
from core.base.exceptions import GameError
from typing import Optional
from core.system.logger import log_msg

class SpecialStageTask:
    def __init__(self, serial):
        self.serial = serial
        self.base = BaseSpecialStage(serial)

    def _stage_to_region_map(self, planet: str) -> tuple[int, int, int, int]:
        stage_region_map = {
            "evo_mine.png": (280, 90, 800, 470),
            "wizard_maze.png": (280, 90, 800, 470),
            "immortal_skull.png": (280, 90, 800, 470),
            "event.png": (280, 90, 800, 470),
        }

        if planet not in stage_region_map:
            raise ValueError(f"未知的 planet 名稱: {planet}")

        return stage_region_map[planet]
    
    def single_battle(self, planet: str, stage: int, loop_mode: bool = False):
        self.base.enter_menu()
        self.base.enter_stage(planet=planet, stage_num=stage)
        if loop_mode:
            self.base.loop_mode_run()
        else:
            self.base.single_mode_run()
    
    def conquer_planet(self, planet: str):
        for stage in range(1, 7):
            self.single_battle(planet=planet, stage=stage, loop_mode=True)

def special_stage_single_game(serial, planet: str, stage: int):
    spc = SpecialStageTask(serial)
    spc.single_battle(planet=planet, stage=stage)