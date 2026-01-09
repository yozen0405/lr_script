from scripts.shared.events.special_stage.base import BaseSpecialStage
from core.actions.vision import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from scripts.shared.utils.retry import connection_retry
from core.base.exceptions import GameError
from typing import Optional
from core.system.logging.logger import log_msg
from scripts.shared.events.special_stage.enum import Planet
from scripts.shared.controller.context import GameContext
from core.system.config import Config

class SpecialStageTask:
    def __init__(self, context: GameContext):
        self.ctx = context
        config = Config()
        self.team_num = config.get_team_num()
        self.base = BaseSpecialStage(self.ctx.serial, self.team_num)

    def enter_menu(self):
        self.base.enter_menu()
    
    def leave_menu(self):
        self.base.leave_menu()

    def _stage_to_region_map(self, planet: str) -> tuple[int, int, int, int]:
        stage_region_map = {
            Planet.EVO_MINE: (235, 250, 250, 135),
            Planet.WIZARD_CUBE: (235, 220, 230, 130),
            Planet.IMMORTAL_SKULL: (235, 220, 230, 130),
            Planet.LIBRARY: (235, 250, 250, 135),
            Planet.COLLAB: (250, 240, 240, 140),
            Planet.LEONARD: (250, 240, 240, 140),
            Planet.CHRISTMAS: (250, 240, 240, 140),
        }

        if planet not in stage_region_map:
            raise ValueError(f"未知的 planet 名稱: {planet}")

        return stage_region_map[planet]
    
    def single_battle(self, planet: str, stage: int, leave_menu: bool = False):
        self.enter_menu()
        crop_region = self._stage_to_region_map(planet=planet)
        region = self.base.find_target_planet(planet=planet, crop_region=crop_region)

        if self.base.enter_stage(stage_num=stage, region=region) == False:
            log_msg(self.ctx.serial, f"第{stage}關已經達到上限")
            return
        else:
            log_msg(self.ctx.serial, f"進入第{stage}關")
        self.base.single_mode_run()
        if leave_menu:
            self.leave_menu()

    def _loop_battle(self, stage: int, region):
        if self.base.enter_stage(stage_num=stage, region=region) == False:
            log_msg(self.ctx.serial, f"第{stage}關已經達到上限")
            return True
        return self.base.loop_mode_run()
    
    def loop_battle(self, planet: str, stage: int):
        self.enter_menu()
        crop_region = self._stage_to_region_map(planet=planet)
        region = self.base.find_target_planet(planet=planet, crop_region=crop_region)

        return self._loop_battle(stage=stage, region=region)

    def conquer_planet(self, planet: str):
        for stage in range(1, 7):
            if not self.loop_battle(planet=planet, stage=stage):
                return

def special_stage_single_game(context: GameContext, planet: str, stage: int, leave_menu: bool = True):
    spc = SpecialStageTask(context)
    spc.single_battle(planet=planet, stage=stage, leave_menu=leave_menu)

def special_stage_loop_game(context: GameContext, planet: str, stage: int):
    spc = SpecialStageTask(context)
    spc.loop_battle(planet=planet, stage=stage)

def special_stage_conquer_planet(context: GameContext, planet: str):
    spc = SpecialStageTask(context)
    spc.conquer_planet(planet=planet)

def special_stage_enter_menu(context: GameContext):
    spc = SpecialStageTask(context)
    spc.enter_menu()

def on_special_stage_event(context: GameContext):
    spc = SpecialStageTask(context)
    spc.enter_menu()
    spc.leave_menu()