from scripts.shared.events.main_stage.base import BaseMainStage
from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from scripts.shared.utils.retry import connection_retry
from scripts.shared.events.main_stage.custom_stages import (
    FirstStage, SecondStage, ThirdStage, 
    AutoStage, FriendStage
)
from core.base.exceptions import GameError
from typing import Optional
from core.system.logger import log_msg
from scripts.shared.events.main_stage.hooks import MainStageHooks
from core.system.config import Config

class MainStageTask:
    def __init__(self, serial):
        self.serial = serial
        self.base_stage = BaseMainStage(serial)
        config = Config()
        self.team_num = config.get_team_num()

    def battle(self, custom_stage: Optional[int] = None, multiplier: int = 1):
        self.base_stage.enter_menu()
        hooks = self._proccess_stage(custom_stage=custom_stage)
        current_stage = BaseMainStage(self.serial, hooks=hooks, is_low=self.is_low, team_num=self.team_num)
        current_stage.enter_battle(multiplier=multiplier)

    def enter_menu(self):
        self.base_stage.enter_menu()

    def _get_hook_class(self, stage_num: int) -> MainStageHooks:
        self.is_low = stage_num < 100

        stage_map = {
            1: FirstStage,
            2: SecondStage,
            3: ThirdStage,
            13: AutoStage,
            30: FriendStage,
        }
        cls = stage_map.get(stage_num, MainStageHooks)
        return cls(self.serial)

    def _proccess_stage(self, custom_stage: Optional[int] = None) -> MainStageHooks:
        stage_num = self.base_stage.enter_stage(custom_stage=custom_stage)
        hooks = self._get_hook_class(stage_num)
        return hooks

def main_stage_finish_new(serial):
    main_stage_task = MainStageTask(serial)
    main_stage_task.battle()

def main_stage_enter_menu(serial):
    main_stage_task = MainStageTask(serial)
    main_stage_task.enter_menu()

def main_stage_finish_custom(serial, custom_stage: int, multiplier: int = 1):
    main_stage_task = MainStageTask(serial)
    main_stage_task.battle(custom_stage=custom_stage, multiplier=multiplier)

