from scripts.shared.events.main_stage.base import BaseMainStage
from core.actions.actions import wait_click, exist_click, exist, wait, wait_vanish, drag, get_pos
from scripts.shared.utils.retry import connection_retry
from scripts.shared.events.main_stage.custom_stages import (
    FirstStage, SecondStage, ThirdStage, 
    AutoStage, FriendStage
)
from core.base.exceptions import GameError
from typing import Optional
from core.system.logger import log_msg

class MainStageTask:
    def __init__(self, serial):
        self.serial = serial
        self.base_stage = BaseMainStage(serial)

    def battle(self, custom_stage: Optional[str] = None):
        self.base_stage.enter_menu()
        stage = self._proccess_stage(custom_stage=custom_stage)
        stage.enter_battle()

    def enter_menu(self):
        self.base_stage.enter_menu()

    def _map_stage_to_class(self, stage_num: int) -> BaseMainStage:
        stage_class = None

        if stage_num == 1:
            stage_class = FirstStage(self.serial)
        elif stage_num == 2:
            stage_class = SecondStage(self.serial)
        elif stage_num == 3:
            stage_class = ThirdStage(self.serial)
        elif stage_num == 13:
            stage_class = AutoStage(self.serial)
        elif stage_num == 30:
            stage_class = FriendStage(self.serial)
        else:
            stage_class = self.base_stage
        return stage_class

    def _proccess_stage(self, custom_stage: Optional[str] = None) -> BaseMainStage:
        stage_num = self.base_stage.enter_stage(custom_stage=custom_stage)
        stage_class = self._map_stage_to_class(stage_num)
        return stage_class

def main_stage_finish_new(serial):
    main_stage_task = MainStageTask(serial)
    main_stage_task.battle()

def main_stage_enter_menu(serial):
    main_stage_task = MainStageTask(serial)
    main_stage_task.enter_menu()

def main_stage_finish_custom(serial, custom_stage: str):
    main_stage_task = MainStageTask(serial)
    main_stage_task.battle(custom_stage=custom_stage)

