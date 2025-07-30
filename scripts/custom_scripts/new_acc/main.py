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

def new_acc_farm(serial, attempts=3):
    for _ in range(attempts):
        phase1(serial)
        phase2(serial)
        phase3(serial)
        phase4(serial)
        phase5(serial)
        phase6(serial)