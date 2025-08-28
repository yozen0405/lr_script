import time
import os
from core.actions.screen import wait_click, exist_click, exist, wait, wait_vanish, back, drag
from core.system.logger import log_msg
from core.base.exceptions import GameError
from scripts.custom_scripts.new_acc.phase6 import Phase6
from scripts.custom_scripts.new_acc.phase5 import Phase5
from scripts.custom_scripts.new_acc.phase4 import Phase4
from scripts.custom_scripts.new_acc.phase3 import Phase3
from scripts.custom_scripts.new_acc.phase2 import Phase2
from scripts.custom_scripts.new_acc.phase1 import Phase1
from scripts.shared.constants import GameView, Settlement, Battle, Confirm, MainView, Leonard, Retry, Positions
from scripts.custom_scripts.new_acc.enum import PreStage, Phase1UI, Quests
from scripts.shared.events.main_stage.enum import MainStage
from scripts.shared.events.gacha.enum import Gacha
from core.system.config import Config

class NewAccFarm:
    def __init__(self, serial):
        self.serial = serial
        cfg = Config()
        self.attempts = cfg.get_cycle_num()
        self.phases = [
            Phase1(serial),
            Phase2(serial),
            Phase3(serial),
            Phase4(serial),
            Phase5(serial),
            Phase6(serial)
        ]

    def detect_phase_index(self) -> int:
        return 1
        # if exist(self.serial, MainView.SETTINGS.value):
        #     return self._handle_main_view()
        # if exist(self.serial, PreStage.MOON.value):
        #     return 1
    
    def _handle_main_view(self):
        if not exist(self.serial, Quests.LONG.value):
            return 1

    # def run(self):
    #     start = self.detect_phase_index() - 1
    #     for i in range(start, len(self.phases)):
    #         self.phases[i].run()
    def run(self, start_phase_idx, start_step_idx):
        start = start_phase_idx - 1
        for i in range(start, len(self.phases)):
            log_msg(self.serial, f"第 {i + 1} 階段開始, 從第 {start_step_idx} 個 step")
            self.phases[i].run(start_idx=start_step_idx)
            start_step_idx = 0

def normal_stage(serial):
    farm = NewAccFarm(serial)
    farm.run(start_phase_idx=2, start_step_idx=2)