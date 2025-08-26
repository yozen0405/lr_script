import time
import os
from core.system.logger import log_msg
from core.base.exceptions import GameError
from scripts.custom_scripts.new_acc.phase6 import phase6
from scripts.custom_scripts.new_acc.phase5 import phase5
from scripts.custom_scripts.new_acc.phase4 import phase4
from scripts.custom_scripts.new_acc.phase3 import phase3
from scripts.custom_scripts.new_acc.phase2 import phase2
from scripts.custom_scripts.new_acc.phase1 import phase1
from core.system.config import Config

class NewAccFarm:
    def __init__(self, serial):
        se

    def _detect_event(self):
        

    def run(self):
        log_msg(self.serial, f"連續刷號開始，預計逕行 {self.attempts} 輪")

        for _ in range(self.attempts):
            phase1(self.serial)
            phase2(self.serial)
            phase3(self.serial)
            phase4(self.serial)
            phase5(self.serial)
            phase6(self.serial)




# def new_acc_farm(serial):
#     cfg = Config()
#     attempts = cfg.get_cycle_num()
#     log_msg(serial, f"連續刷號開始，預計逕行 {attempts} 輪")

#     for _ in range(attempts):
#         phase1(serial)
#         # phase2(serial)
#         # phase3(serial)
#         # phase4(serial)
#         # phase5(serial)
#         # phase6(serial)